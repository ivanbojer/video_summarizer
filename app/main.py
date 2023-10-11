import gradio as gr
import json
import secrets
from fastapi import FastAPI
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.requests import Request
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.middleware.sessions import SessionMiddleware

from app import ignoreSSL
from app import video_summarizer as vid
from app import logger

OBFUSCATED_MNT_POINT = secrets.token_urlsafe(30)

# Load config values
with open(r'config.json') as config_file:
    config_details = json.load(config_file)

# Load secret values
with open(r'client_secret.json') as secret_file:
    secret_details = json.load(secret_file)

GOOGLE_CLIENT_ID = secret_details['web']['client_id'] or None
GOOGLE_CLIENT_SECRET = secret_details['web']['client_secret'] or None
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException('Missing sec configuration')

# Set up oauth
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)


def summarize_text(video_id, progress=gr.Progress()):
    progress(float(0.0), desc="Starting...")
    summary = vid.test_load_final_summary()
    # summary = vid.transcribe_video(video_id, False, progress)
    return gr.Button(interactive=False), summary 

with gr.Blocks() as demo:
    with gr.Column():
        with gr.Group():
            inp = gr.Text(label="Video id:")
            btn = gr.Button("Transcribe")
        with gr.Box():
            out = gr.TextArea(label="Summary output:")
        
        btn.click(fn=summarize_text, inputs=inp, outputs=[btn,out])


app = FastAPI()

SECRET_KEY = config_details['SECRET_KEY'] or None
if SECRET_KEY is None:
    raise 'Missing SECRET_KEY'
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


@app.route('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')  # This creates the url for the /auth endpoint
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.route('/auth')
async def auth(request: Request):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        return RedirectResponse(url='/')
    # user_data = await oauth.google.parse_id_token(request, access_token)
    # request.session['user'] = dict(user_data)
    request.session['user'] = access_token.get('userinfo')
    return RedirectResponse(url='/')


@app.get('/')
async def public(request: Request):
    user = request.session.get('user')
    if user:
        name = user.get('name')
        email = user.get('email')
        logger.logger.info('Logged in user: {} [{}]'.format(name, email))
        return RedirectResponse(url='/{}'.format( OBFUSCATED_MNT_POINT ))
    return HTMLResponse('<a href=/login>Login</a>')

    # return RedirectResponse(url='/gradio')

@app.route('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

gradio_app = gr.mount_gradio_app(app, demo.queue(), '/{}'.format( OBFUSCATED_MNT_POINT) )
    