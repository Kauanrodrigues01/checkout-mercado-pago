from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from payments.router import router

app = FastAPI(
    title='Checkout Mercado Pago',
    description='Fazendo integração com a API do Mercado Pago'
)
app.include_router(router)

templates = Jinja2Templates(directory='templates')

@app.get('/', response_class=HTMLResponse)
async def checkout_page(request: Request):
    return templates.TemplateResponse(name='checkout.html', context={'request': request})
