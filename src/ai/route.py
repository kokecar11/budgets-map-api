import json
from fastapi import APIRouter
from .service import AIService
from .schemas import PostHumanQueryPayload, PostHumanQueryResponse
from src.dependencies import db_dependency

AIRouter = APIRouter()


@AIRouter.post("/human-query")
async def get_human_query(payload: PostHumanQueryPayload, db: db_dependency):
    ai_service = AIService(db)
    sql_query = ai_service.human_query_to_sql(payload.human_query)
    if not sql_query:
        return {"error": "Falló la generación de la consulta SQL"}
    result_dict = json.loads(sql_query)

    result = await ai_service.query(result_dict["sql_query"])

    answer = await ai_service.build_answer(result, payload.human_query)
    if not answer:
        return {"error": "Falló la generación de la respuesta"}
    print(answer)
    return {"answer": answer}
