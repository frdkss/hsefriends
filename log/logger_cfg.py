from loguru import logger

inits_logger = logger.bind(category='init')
logger.add(r'log\inits.log', format='{name} | {line} | {time} | {level} | {message}', rotation="00:00",
           compression="zip", filter=lambda record: record["extra"].get("category") == "init")

command_logger = logger.bind(category='command')
logger.add(r'log\commands.log', format='{name} | {line} | {time} | {level} | {message}', rotation="00:00",
           compression="zip", filter=lambda record: record["extra"].get("category") == "command")

callback_logger = logger.bind(category='callback')
logger.add(r'log\callbacks.log', format='{name} | {line} | {time} | {level} | {message}', rotation="00:00",
           compression="zip", filter=lambda record: record["extra"].get("category") == "callback")

registration_logger = logger.bind(category='reg')
logger.add(r'log\callbacks.log', format='{name} | {line} | {time} | {level} | {message}', rotation="00:00",
           compression="zip", filter=lambda record: record["extra"].get("category") == "reg")

inline_kb_logger = logger.bind(category='inline_kb')
logger.add(r'log\callbacks.log', format='{name} | {line} | {time} | {level} | {message}', rotation="00:00",
           compression="zip", filter=lambda record: record["extra"].get("category") == "inline_kb")

default_kb_logger = logger.bind(category='default_kb')
logger.add(r'log\callbacks.log', format='{name} | {line} | {time} | {level} | {message}', rotation="00:00",
           compression="zip", filter=lambda record: record["extra"].get("category") == "default_kb")