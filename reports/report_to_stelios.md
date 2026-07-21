# Report to Stelios

## Executive summary

This project implements end to end market data pipe line for Owl Analytics. It collects hourly candlestick data for ten cryptocurrency pairs from the public Binance market-data API, deliberately damages a copy to simulate realistic quality problems, cleans the damaged data with pandas, and analyses the full cleaned dataset with PySpark and Spark SQL. The software separates ot the collection, qu;ality and control of the data so that each phase is individualy understood to generate a satisfied outcome. 

## Data collection and concurrency

The Team 1 program requests 1,000 one-hour kline records for each of ten specified symbols, giving exactly 10,000 records when Binance returns the expected response. Each API record is mapped into named CSV fields, including readable UTC opening and closing timestamps, OHLC prices, volumes and trade count. The program validates every per-symbol response and checks the final row count before writing `clean_market_data.csv`. This prevents a partial download from silently becoming the official dataset.

The downloader provides both serial and multithreaded implementations, this steo also provides a comparison between multithreaded and serial downloads of the data. The serial version downloads one symbol after another. The threaded version uses `ThreadPoolExecutor`, which is appropriate because network requests spend much of their time waiting for remote responses rather than using the processor. A semaphore limits the number of requests that can be active concurrently. A separate sliding-window rate limiter stores recent request times and prevents the application from starting more than 100 requests in any 60-second period. Although this project makes only ten requests per run, implementing the limit demonstrates safe behaviour and makes the code easier to extend.

A benchmark times only the API download stage with `time.perf_counter()` and writes serial and threaded runtimes to `runtime_comparison.csv`. Threading is normally faster for this workload because requests overlap, but it does not guarantee a fixed improvement; network congestion, server response time and thread overhead can affect the result.

The log is protected with a lock because several worker threads may finish at nearly the same time. Without protection, writes could interleave and make the log difficult to read or, on some systems, damage lines. The log records request start, completion, row counts, errors, rate-limit waits and the final CSV write. This makes failures traceable.

## Data-quality process

Dara’s corruption stage represents missing values, dropped records, duplicate rows, text in numeric columns, invalid timestamps, inconsistent symbol formats and negative volumes. Team 2 loads this messy file, prints its dimensions, first ten records and original data types, then reports missing values by column. Numeric conversion uses `errors='coerce'`, which turns unconvertible values such as `unknown` into missing values instead of crashing. Timestamp conversion follows the same safe approach. Symbols are uppercased, trimmed and stripped of separators so forms such as `btcusdt`, ` BTCUSDT ` and `BTC/USDT` become `BTCUSDT`.

The program removes duplicates and rows that cannot be repaired reliably. It rejects missing essential values, negative numeric values, invalid price ranges and negative trade counts. It then engineers `price_range`, `price_change`, `percent_change` and `candle_direction`. A before-and-after quality report records the number of problems detected, rows removed, remaining missing values, duplicate count and output size. This gives reviewers evidence that cleaning was deliberate rather than accidental.

Pandas is used for a balanced 50-row check: five records per symbol. This is useful for quick inspection and simple grouped summaries, but it is explicitly not the final market analysis. A small balanced sample is easier to inspect and avoids one symbol dominating the check.

## Spark analytics

Zehra requested Spark for the complete cleaned dataset because the analytics stage is intended to demonstrate scalable processing and SQL-based aggregation. The notebook starts a Spark session, loads the full cleaned CSV, verifies its schema and count, and registers a temporary view called `market_data`. It verifies or recreates the engineered measures and adds hour, date and day-of-week features.

The notebook contains more than six meaningful Spark SQL queries. These include record and price summaries, volatility ranking, trading-activity ranking, candle-direction counts, extreme hourly movements, hourly activity, weekday activity and daily market movement. The final summary ranks every symbol with average closing price, average range, standard deviation of percentage change, total trades, total volume and average percentage change. It is exported as `spark_market_summary.csv`.

The most important interpretation is that volatility and activity are different concepts. A symbol may attract many trades but move within a comparatively narrow percentage range, while another may be less active yet more volatile. Time-based queries also reveal when activity and large movements occurred. Because Binance returns the latest available candles, exact rankings depend on the extraction date and should be read from the saved output of the final run.

## Reliability and limitations

The pipeline provides validation, thread-safe logs, deterministic corruption, a cleaning report and reproducible analytics code. Its main limitation is reliance on a live public API. A temporary outage or API change can prevent collection. CSV is also suitable for this coursework but a typed columnar format such as Parquet would be preferable at larger scale. Overall, the project supplies a complete, inspectable handoff from raw API data to a ranked market summary.
