from fastapi import FastAPI, Request, status
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.form()
    from_number = data.get('From', '')
    body = data.get('Body', '')
    # TODO: Integrar con el motor conversacional y memoria
    print(f"Mensaje recibido de {from_number}: {body}")
    return PlainTextResponse("OK", status_code=status.HTTP_200_OK)

# TODO: Proteger endpoint y validar autenticidad de Twilio 