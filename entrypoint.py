# import the flask web framework
from flask import Flask
import json
import redis as redis
from flask import Flask, request
from loguru import logger
from flask import jsonify

# Definition of constants for testing
HISTORY_LENGTH = 10
DATA_KEY = "engine_temperature"

# create a Flask server, and allow us to interact with it using the app variable
app = Flask(__name__)


# define an endpoint which accepts POST requests, and is reachable from the /record endpoint
@app.route('/record', methods=['POST'])
def record_engine_temperature():
    payload = request.get_json(force=True)
    logger.info(f"(*) record request --- {json.dumps(payload)} (*)")

    engine_temperature = payload.get("engine_temperature")
    logger.info(f"engine temperature to record is: {engine_temperature}")

    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    database.lpush(DATA_KEY, engine_temperature)
    logger.info(f"stashed engine temperature in redis: {engine_temperature}")

    while database.llen(DATA_KEY) > HISTORY_LENGTH:
        database.rpop(DATA_KEY)
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    logger.info(f"engine temperature list now contains these values: {engine_temperature_values}")

    logger.info(f"record request successful")
    return {"success": True}, 200

# define an endpoint which accepts POST requests, and is reachable from the /collect endpoint
@app.route('/collect', methods=['GET'])
def collect_engine_data():
  """
  This endpoint retrieves and returns current and average engine temperature data.
  """
  database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

  # Get the latest engine temperature
  current_engine_temperature = database.lindex(DATA_KEY, -1)

  # Calculate the average engine temperature
  engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
  if engine_temperature_values:
    average_engine_temperature = sum(float(value) for value in engine_temperature_values) / len(engine_temperature_values)
  else:
    average_engine_temperature = None  # No data available

  # Prepare the response data
  response_data = {
      "current_engine_temperature": current_engine_temperature,
      "average_engine_temperature": average_engine_temperature
  }

  logger.info(f"Engine data collected: {response_data}")
  return jsonify(response_data), 200