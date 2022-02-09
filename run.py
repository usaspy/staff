from api import app
import config as cfg

if __name__ == '__main__':
    app.run(host=cfg.RESTFul_API_HOST, port=cfg.RESTFul_API_PORT, debug=False)