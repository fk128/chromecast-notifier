# Chromecast Notifier

Chromecast notifier using [Google TTS](https://cloud.google.com/text-to-speech). 

Obtain Google credentials file from Google Cloud console and set path with env variable (or create .env file)

```bash
export GOOGLE_APPLICATION_CREDENTIALS="./text to speech-google-cred.json"
```

Set up conda environment

```bash
conda create --name chromecast-notifier python=3.7
conda activate chromecast-notifier
```

```bash
git clone https://github.com/fk128/chromecast-notifier.git
cd chromecast-notifier
pip install -e .
```

Start server on http://localhost:8084/
```bash
python -m chromecast_notifier.server
```

Check API docs http://localhost:8084/docs

`curl -X GET "http://localhost:8084/notify?text=hello"`

`curl -X POST "http://localhost:8084/notify" -d "text=hello"`