import gradio as gr
import json
import secrets
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.requests import Request
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.middleware.sessions import SessionMiddleware

from app import ignoreSSL
from app import video_summarizer as vid
from app import logger
from app import my_prompt

OBFUSCATED_MNT_POINT = secrets.token_urlsafe(30)

# Load config values
with open(r'config.json') as config_file:
    config_details2 = json.load(config_file)


GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID') or None
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET') or None
SECRET_KEY = os.getenv('SECRET_KEY') or None
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None or SECRET_KEY is None:
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


def summarize_text(video_id, batch_prompt, final_prompt, progress=gr.Progress()):
    progress(float(0.0), desc="Starting...")
    # summary = vid.test_load_final_summary()

    summary = vid.transcribe_video(video_id=video_id, batch_prompt=batch_prompt, final_prompt=final_prompt, progress=progress)
    return gr.Button(interactive=False), summary 


with gr.Blocks() as demo:
    with gr.Box():
        with gr.Row():
            with gr.Group():
                video_id = gr.Text(label="Video id:")
                batch_prompt = gr.Textbox(label="Batch prompt:", value=my_prompt.SYSTEM_PROMPT_BATCHES)
                final_prompt = gr.Textbox(label="Final prompt:", value=my_prompt.SYSTEM_PROMPT_FINAL)
                btn = gr.Button("Transcribe")
            with gr.Group():
                out = gr.TextArea(label="Summary output:", lines=34)
            
            btn.click(fn=summarize_text, inputs=[video_id, batch_prompt, final_prompt], outputs=[btn, out])


app = FastAPI()


def is_authorized( user_email ):
    return user_email in ['ivan@bojerco.com'] 


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    '''The middleware that enforces authentication on our gradio app'''
    
    # Skip check for obvious mounts (like '/login')
    if request.url.path.startswith( ('/login', '/auth', '/logout') ):
        logger.logger.debug('In URL Path: {}'.format( request.url.path ))
        return await call_next(request)

    user = request.session.get("user")
    access_token = request.session.get("access_token")
    refresh_token = request.session.get("refresh_token")

    if not user or not access_token or not refresh_token:
        logger.logger.warn('User is not authenticated, redirecting to login page')
        return RedirectResponse(url='/login')
    
    return await call_next(request)

@app.route('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')  # This creates the url for the /auth endpoint
    return await oauth.google.authorize_redirect(request, redirect_uri, access_type='offline', prompt='consent')


@app.route('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    request.session.pop('access_token', None)
    request.session.pop('refresh_token', None)
    # return {"message": "You have been logged out."}
    return HTMLResponse('<p>You have been logged out.</p><a href=/login>Login again</a>')


@app.route('/support_access')
async def get_support_bundle(request: Request):
    user = request.session.get('user')

    if user and is_authorized(user['email']):
        return FileResponse('file.log')
    else:
        return RedirectResponse(url='logout')
    

@app.route('/support_access_final')
async def get_support_bundle(request: Request):
    user = request.session.get('user')

    if user and is_authorized(user['email']):
        try:
            path = './temp_data'
            files = os.listdir(path)
            files_new = []
            for f in files:
                if f.endswith('FINAL_SUMMARY.txt'):
                    files_new.append( f )

            mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
            most_recent_file = list(sorted(files_new, key=mtime))[-1]
            logger.logger.info('Retrieving file: {}/{}'.format(path, most_recent_file))

            return FileResponse( '{}/{}'.format(path, most_recent_file))
        except Exception as e:
            logger.logger.warning('No final files: {}'.format( e ))
    else:
        return RedirectResponse(url='logout')


@app.route('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        return RedirectResponse(url='/')

    user = token.get('userinfo')

    if is_authorized(user['email']):
        request.session['user'] = user
        request.session['access_token'] = token['access_token']
        request.session['refresh_token'] = token['refresh_token']
        return RedirectResponse(url='/')
    
    logger.logger.warn('Detected unauthorized access by {}'.format( user ))
    return RedirectResponse(url='logout')


@app.get('/')
async def public(request: Request):
    user = request.session.get('user')
    if user:
        name = user.get('name')
        email = user.get('email')
        logger.logger.info('Logged in user: {} [{}]'.format(name, email))
        return RedirectResponse(url='/{}'.format( OBFUSCATED_MNT_POINT ))
    
    return HTMLResponse('<a href=/login>Login</a>')


gradio_app = gr.mount_gradio_app(app, demo.queue(), '/{}'.format( OBFUSCATED_MNT_POINT) )
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
    