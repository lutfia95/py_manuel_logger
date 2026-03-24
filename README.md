# ManuelLogger

Small, dependency-free Python logger for readable terminal output.

It provides:

- colored log levels
- timestamps
- application names in each message
- optional automatic log file output
- convenience helpers like `banner()`, `section()`, `kv()`, and `pair()`

## Use Cases

This logger is useful when you want cleaner console output without configuring Python's built-in `logging` module.

Typical use cases:

- CLI tools
- small automation scripts
- ETL or data-processing jobs
- quick debugging during development
- deployment scripts
- status output for internal tools

## Quick Start

Use the logger directly from `manuel_logging.py`:

```python
from manuel_logging import ManuelLogger

logger = ManuelLogger(name="my-app", level="info")

logger.info("Application started")
logger.success("Connected successfully")
logger.warning("Retrying request")
logger.error("Something failed")
```

If you want to control the level without editing Python code every time:

```python
from manuel_logging import ManuelLogger

logger = ManuelLogger(name="correction", log_file="worker.log")
```

Then set the level from your shell:

```bash
export MANUEL_LOG_LEVEL=debug
python your_script.py
```

Write the same logs to a file:

```python
from manuel_logging import ManuelLogger

logger = ManuelLogger(name="my-app", level="info", log_file="logs/app.log")

logger.info("Application started")
logger.success("This is written to the terminal and logs/app.log")
```

## Log Levels

Supported log levels:

- `debug`
- `info`
- `success`
- `warning`
- `error`
- `critical`

You can control the minimum visible level:

```python
from manuel_logging import ManuelLogger

logger = ManuelLogger(name="worker", level="warning")

logger.debug("Hidden")
logger.info("Hidden")
logger.warning("Shown")
logger.error("Shown")
```

You can also change it later:

```python
logger.set_level("debug")
logger.debug("Debug logging is now enabled")
```

### What Each Level Means

#### `debug`

Use `debug()` for developer-focused details that help troubleshoot behavior.

Typical use cases:

- raw API responses
- variable values
- loop progress
- branch decisions
- temporary diagnostics during development

```python
logger.debug("Fetched 250 rows from source API")
logger.debug(f"Current batch index: {batch_index}")
```

#### `info`

Use `info()` for normal runtime progress and expected events.

Typical use cases:

- job started
- file loaded
- process step started
- user action completed normally

```python
logger.info("Correction job started")
logger.info("Loaded source file successfully")
```

#### `success`

Use `success()` when something finished correctly and you want that message to stand out positively.

Typical use cases:

- file saved
- upload completed
- task finished
- database write succeeded

```python
logger.success("Results exported successfully")
logger.success("Upload completed")
```

#### `warning`

Use `warning()` when something is not ideal, but the program can still continue.

Typical use cases:

- missing optional values
- retrying an operation
- fallback logic triggered
- unexpected but non-fatal input

```python
logger.warning("API timeout, retrying request")
logger.warning("Optional field 'middle_name' is missing")
```

#### `error`

Use `error()` when one operation failed and needs attention.

Typical use cases:

- request failed
- validation failed
- file could not be processed
- database insert failed

```python
logger.error("Could not save corrected output")
logger.error("Validation failed for input row")
```

#### `critical`

Use `critical()` for severe failures where the whole workflow may need to stop.

Typical use cases:

- application cannot start
- database is unavailable
- configuration is broken
- unrecoverable pipeline failure

```python
logger.critical("Database connection unavailable, stopping worker")
logger.critical("Missing required configuration, aborting startup")
```

### `info()` vs `kv()`

Use `info()` for sentence-style messages:

```python
logger.info("Loaded correction file")
```

Use `kv()` for labeled values:

```python
logger.kv("file_name", "corrections.csv")
logger.kv("row_count", 128)
```

A practical pattern is to combine them:

```python
logger.info("Loaded correction file")
logger.kv("file_name", "corrections.csv")
logger.kv("row_count", 128)
```

## Python Usage Examples

### 1. Basic script logging

```python
from manuel_logging import ManuelLogger

logger = ManuelLogger(name="import-job")

logger.info("Starting import")
logger.success("Import finished")
```

### 2. Logging key/value data

Useful for configs, IDs, counters, and runtime state.

```python
from manuel_logging import ManuelLogger

logger = ManuelLogger(name="sync-service")

logger.kv("user_id", 42)
logger.kv("records_processed", 128)
logger.kv("environment", "production")
```

Use `kv()` when you want readable metadata instead of a sentence.

### 3. Logging workflow steps

```python
from manuel_logging import ManuelLogger

logger = ManuelLogger(name="pipeline")

logger.section("Extract")
logger.info("Reading source file")

logger.section("Transform")
logger.pair("raw.csv", "clean.csv")

logger.section("Load")
logger.success("Upload complete")
```

Use `section()` to separate stages in a script, and `success()` when one stage completes correctly.

### 4. Logging missing values

```python
from manuel_logging import ManuelLogger

logger = ManuelLogger(name="validator")

email = None

if not email:
    logger.missing("email", email)
```

Use `missing()` as a shortcut for common validation warnings.

### 5. Logging exceptions

```python
from manuel_logging import ManuelLogger

logger = ManuelLogger(name="api-client")

try:
    result = 10 / 0
except Exception as exc:
    logger.exception("Request failed", exc)
```

Use `exception()` when you want the error message plus traceback in the log output.

### 6. Printing a banner

```python
from manuel_logging import ManuelLogger

logger = ManuelLogger(name="setup")
logger.banner("Initial Setup")
```

Use `banner()` for major script starts, setup phases, or one-off jobs where you want a visible heading.

## Configuration

`ManuelLogger` accepts these options:

```python
ManuelLogger(
    name="app",
    level="info",
    log_file=None,
    use_color=None,
    show_time=True,
    show_level=True,
    stream=sys.stderr,
)
```

### Parameters

- `name`: label shown in every log line
- `level`: minimum visible log level
  If omitted, the logger uses `MANUEL_LOG_LEVEL`, then falls back to `info`.
- `log_file`: optional path for automatic file logging
- `use_color`: enable or disable ANSI colors manually
- `show_time`: show timestamps
- `show_level`: show the log level label
- `stream`: output stream, default is `sys.stderr`

## File Logging

To automatically persist logs:

```python
from manuel_logging import ManuelLogger

logger = ManuelLogger(
    name="worker",
    level="debug",
    log_file="logs/worker.log",
)

logger.info("Job started")
logger.kv("batch_id", 123)
logger.success("Job finished")
```

Behavior:

- parent directories are created automatically if needed
- logs are appended to the file
- file output does not include ANSI color codes
- each write is flushed immediately
- `exception()` writes the error message and full traceback

## Changing The Level Without Editing Code

Instead of changing this every time:

```python
logger = ManuelLogger(name="correction", level="info", log_file="worker.log")
```

you can leave `level` out:

```python
logger = ManuelLogger(name="correction", log_file="worker.log")
```

and control it from the terminal:

```bash
MANUEL_LOG_LEVEL=debug python your_script.py
```

or:

```bash
MANUEL_LOG_LEVEL=warning python your_script.py
```

## Minimal Example

```python
from manuel_logging import ManuelLogger

def main():
    logger = ManuelLogger(name="demo", level="debug")
    logger.banner("Demo Run")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.success("Success message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

if __name__ == "__main__":
    main()
```

## Notes

- No external dependencies are required.
- Colors are automatically disabled when the output stream does not support them.
- Setting the `NO_COLOR` environment variable disables colored output.
