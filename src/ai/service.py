import openai
from typing import Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from src.database import get_schema
from src.settings import get_settings


class AIService:
    def __init__(self, db):
        self.settings = get_settings()
        self.openai = openai.api_key = self.settings.OPENAI_API_KEY
        self.db = db
        self.db_schema = get_schema()

    def human_query_to_sql(self, human_query: str):
        database_schema = self.db_schema
        system_message = f"""
            Given the following schema, write a SQL query that retrieves the requested information. 
            Return the SQL query inside a JSON structure with the key "sql_query".
            <example>{{
                "sql_query": "SELECT * FROM users WHERE age > 18;"
                "original_query": "Show me all users older than 18 years old."
            }}
            </example>
            <schema>
            {database_schema}
            </schema>
        """
        user_message = human_query

        response = openai.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
        )

        return response.choices[0].message.content

    async def build_answer(
        self, result: list[dict[str, Any]], human_query: str
    ) -> str | None:

        system_message = f"""
            Given a users question and the SQL rows response from the database from which the user wants to get the answer,
            write a response to the user's question.
            <user_question> 
            {human_query}
            </user_question>
            <sql_response>
            ${result} 
            </sql_response>
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
            ],
        )

        return response.choices[0].message.content

    async def query(self, sql_query: str):
        print(sql_query)
        try:
            result = self.db.execute(text(sql_query))
            self.db.commit()
            return [dict(row._mapping) for row in result.fetchall()]
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Error executing query: {e}")
            return None
