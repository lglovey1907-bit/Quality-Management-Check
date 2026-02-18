# Streamlit Configuration

This folder contains configuration for the Streamlit web application.

## config.toml

Main configuration file with settings for:
- **Upload limits**: 500MB max per file
- **Server settings**: Port 8501, CORS disabled
- **Performance**: Websocket compression, fast reruns
- **Timeouts**: 600 seconds for long-running analyses

## Customization

Edit `config.toml` to change:

### Increase upload limit (for very large PDFs):
```toml
[server]
maxUploadSize = 1000  # 1GB
```

### Change port:
```toml
[server]
port = 8080  # Different port
```

### Enable dark theme:
```toml
[theme]
base = "dark"
```

## Official Documentation

For all available options, see:
https://docs.streamlit.io/library/advanced-features/configuration

## Troubleshooting

If upload errors persist after changing settings:
1. Restart the Streamlit app
2. Clear browser cache
3. See `/TROUBLESHOOTING_UPLOAD.md` for detailed help
