import openai
import json
from typing import Any
from src.exceptions import BadRequestError
from .repository import AIRepository
from src.transaction.services import TransactionService
from src.database import get_schema
from src.settings import get_settings


class AIService:
    def __init__(
        self, ai_repository: AIRepository, transaction_service: TransactionService
    ):
        self.ai_repository = ai_repository
        self.transaction_service = transaction_service
        self.settings = get_settings()
        self.openai = openai.api_key = self.settings.OPENAI_API_KEY

    async def human_query_to_sql(self, human_query: str):
        database_schema = self.ai_repository.get_schema()
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

    async def get_human_query(self, human_query: str):
        sql_query = await self.human_query_to_sql(human_query)
        if not sql_query:
            return BadRequestError("Failed to generate SQL query")
        result_dict = json.loads(sql_query)

        result = await self.ai_repository.query(result_dict["sql_query"])
        answer = await self.build_answer(result, human_query)
        if not answer:
            return BadRequestError("Failed to generate answer")
        return answer

    async def generate_budget_recommendation(
        self, user_id: str, budget_type: str
    ) -> str:
        user_budget_data = await self.transaction_service.get_summary_by_user_id(
            user_id
        )
        if not user_budget_data:
            return BadRequestError(
                "Not enough data to generate a recommendation. Please add more transactions."
            )
        formatted_data = self._format_budget_data(user_budget_data, budget_type)
        system_message = f"""
            You are a financial advisor specialized in personal budgeting.
            Analyze the user's budget data and provide a concise recommendation (maximum 2–3 sentences).
            Be specific, using percentages or amounts based on the user's actual financial data.
            Focus exclusively on the most impactful action they should take, tailored to their budget type.
            
            <user_budget_data>
            {formatted_data}
            </user_budget_data>
        """

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                ],
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating budget recommendation: {e}")
            return "No se pudo generar una recomendación en este momento. Inténtalo más tarde."

    def _format_budget_data(
        self, budget_data: dict[str, Any], budget_type: str = "balanced"
    ) -> str:
        formatted_text = []

        formatted_text.append(f"Tipo de Presupuesto: {budget_type}")
        formatted_text.append(f"\nBalance General:")

        if hasattr(budget_data, "income") and hasattr(
            budget_data.income, "current_month"
        ):
            income_value = budget_data.income.current_month
            formatted_text.append(f"- Ingreso total: {income_value}")

        if hasattr(budget_data, "expense") and hasattr(
            budget_data.expense, "current_month"
        ):
            expense_value = budget_data.expense.current_month
            formatted_text.append(f"- Gastos totales: {expense_value}")

        if hasattr(budget_data, "saving") and hasattr(
            budget_data.saving, "current_month"
        ):
            saving_value = budget_data.saving.current_month
            formatted_text.append(f"- Ahorros totales: {saving_value}")

        if hasattr(budget_data, "debt") and hasattr(budget_data.debt, "current_month"):
            debt_value = budget_data.debt.current_month
            formatted_text.append(f"- Deudas totales: {debt_value}")

        if (
            hasattr(budget_data, "income")
            and hasattr(budget_data.income, "current_month")
            and budget_data.income.current_month > 0
        ):
            income_value = budget_data.income.current_month

            if hasattr(budget_data, "expense") and hasattr(
                budget_data.expense, "current_month"
            ):
                expense_value = budget_data.expense.current_month
                expense_percentage = (expense_value / income_value) * 100
                formatted_text.append(
                    f"- Porcentaje de gastos: {expense_percentage:.2f}%"
                )

            if hasattr(budget_data, "saving") and hasattr(
                budget_data.saving, "current_month"
            ):
                saving_value = budget_data.saving.current_month
                saving_percentage = (saving_value / income_value) * 100
                formatted_text.append(
                    f"- Porcentaje de ahorro: {saving_percentage:.2f}%"
                )

            if hasattr(budget_data, "debt") and hasattr(
                budget_data.debt, "current_month"
            ):
                debt_value = budget_data.debt.current_month
                debt_percentage = (debt_value / income_value) * 100
                formatted_text.append(f"- Porcentaje de deuda: {debt_percentage:.2f}%")

        formatted_text.append(f"\nObjetivos para Presupuesto {budget_type}:")

        if budget_type == "saving":
            formatted_text.append(
                "- Maximizar el ahorro (meta recomendada: 25-40% del ingreso)"
            )
            formatted_text.append("- Minimizar gastos no esenciales")
            formatted_text.append("- Establecer metas de inversión a largo plazo")
        elif budget_type == "balanced":
            formatted_text.append("- Mantener equilibrio entre gastos y ahorros")
            formatted_text.append("- Ahorro recomendado: 15-25% del ingreso")
            formatted_text.append(
                "- Permitir gastos moderados en entretenimiento y lujos"
            )
        elif budget_type == "debt":
            formatted_text.append("- Priorizar el pago de deudas de alto interés")
            formatted_text.append("- Limitar nuevos gastos no esenciales")
            formatted_text.append("- Establecer un pequeño fondo de emergencias")
            formatted_text.append("- Meta de ahorro mínimo: 5-10% del ingreso")

        if "expense_categories" in budget_data:
            formatted_text.append("\nCategorías de Gastos:")
            for category, amount in budget_data.get("expense_categories", {}).items():
                formatted_text.append(f"- {category}: {amount}")

        return "\n".join(formatted_text)
