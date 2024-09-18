from loguru import logger

inits_logger = logger.bind(category='init')
logger.add(r'log\inits.log', format='{name} | {line} | {time} | {level} | {message}', rotation="00:00",
           compression="zip", filter=lambda record: record["extra"].get("category") == "init")
