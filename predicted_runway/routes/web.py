import logging

import flask as f
from flask import send_from_directory
from marshmallow import ValidationError

from met_update_db import repo as met_repo

from predicted_runway.adapters import airports as airports_api
# from predicted_runway.adapters.met import api as met_api
from predicted_runway.config import DESTINATION_ICAOS
from predicted_runway.domain import predictor
from predicted_runway.routes.factory import RunwayPredictionInputFactory, \
    RunwayConfigPredictionInputFactory
from predicted_runway.routes.schemas import RunwayPredictionInputSchema, \
    RunwayConfigPredictionInputSchema, RunwayPredictionOutputSchema, \
    RunwayConfigPredictionOutputSchema

_logger = logging.getLogger(__name__)


web_blueprint = f.Blueprint('web', __name__)


@web_blueprint.route('/static/<path:path>')
def send_report(path):
    return send_from_directory('static', path)


@web_blueprint.route("/")
def index():
    return f.render_template('index.html',
                             destination_airports=airports_api.get_destination_airports())


@web_blueprint.route("/runway-prediction/arrivals", methods=['GET', 'POST'])
def runway_prediction():
    if f.request.method == 'GET':
        return _get_runway_prediction()

    if f.request.method == 'POST':
        return _post_runway_prediction()


def _message_invalid_request_exception(exc: Exception) -> str:
    mapper = {
        ValidationError: str(exc),
        met_repo.METNotAvailable:
            f"There is no meteorological information available for the provided timestamp. "
            f"Please try again with different value."
    }
    return mapper.get(type(exc), "Invalid input.")


def _runway_prediction_input_from_input_data(input_data):
    validated_input = RunwayPredictionInputSchema().load(input_data)

    return RunwayPredictionInputFactory.create(**validated_input)


def _post_runway_prediction():
    try:
        prediction_input = _runway_prediction_input_from_input_data(input_data=dict(f.request.form))
    except Exception as exc:
        message = _message_invalid_request_exception(exc)
        return _load_runway_prediction_template_with_warning(message)

    return f.redirect(f.url_for('web.runway_prediction', **prediction_input.to_dict()))


def _get_runway_prediction():

    try:
        prediction_input = _runway_prediction_input_from_input_data(input_data=f.request.args)
    except Exception as exc:
        _logger.exception(exc)
        message = _message_invalid_request_exception(exc)
        return _load_runway_prediction_template_with_warning(message)

    try:
        prediction_output = predictor.get_runway_prediction_output(prediction_input)
    except Exception as exc:
        _logger.exception(exc)
        return _load_runway_prediction_template_with_warning(
            "Something went wrong during the prediction. Please try again later."
        )

    result = RunwayPredictionOutputSchema(prediction_input, prediction_output).to_web_response()

    return _load_runway_prediction_template(result=result)


def _runway_config_prediction_input_from_input_data(input_data):
    validated_input = RunwayConfigPredictionInputSchema().load(input_data)

    return RunwayConfigPredictionInputFactory.create(**validated_input)


def _get_runway_config_prediction():

    try:
        prediction_input = _runway_config_prediction_input_from_input_data(input_data=f.request.args)
    except Exception as exc:
        _logger.exception(exc)
        message = _message_invalid_request_exception(exc)
        return _load_runway_config_prediction_template_with_warning(message)

    try:
        prediction_output = predictor.get_runway_config_prediction_output(prediction_input)
    except Exception as exc:
        _logger.exception(exc)
        return _load_runway_config_prediction_template_with_warning(
            "Something went wrong during the prediction. Please try again later."
        )

    result = RunwayConfigPredictionOutputSchema(prediction_input, prediction_output).to_web_response()

    return _load_runway_config_prediction_template(result=result)


def _post_runway_config_prediction():
    try:
        prediction_input = _runway_config_prediction_input_from_input_data(
            input_data=dict(f.request.form))
    except Exception as exc:
        _logger.exception(exc)
        message = _message_invalid_request_exception(exc)
        return _load_runway_config_prediction_template_with_warning(message)

    return f.redirect(f.url_for('web.runway_config_prediction',
                                **prediction_input.to_dict()))


@web_blueprint.route("/runway-config-prediction/arrivals", methods=['GET', 'POST'])
def runway_config_prediction():
    if f.request.method == 'GET':
        return _get_runway_config_prediction()

    if f.request.method == 'POST':
        return _post_runway_config_prediction()


@web_blueprint.route("/airports-data/<string:search>", methods=['GET'])
def airports_data(search: str):
    airports = airports_api.get_airports(search=search)

    result = [{"title": airport.title} for airport in airports]

    return f.jsonify(result), 200


@web_blueprint.route("/last-taf-end-time/<string:destination_icao>", methods=['GET'])
def get_last_taf_end_time(destination_icao: str):
    if destination_icao not in DESTINATION_ICAOS:
        return {
           "error": f"destination_icao {destination_icao} is not supported. "
                    f"Please choose one of {', '.join(DESTINATION_ICAOS)}"
        }, 404

    try:
        end_time_datetime = met_repo.get_last_taf_end_time(airport_icao=destination_icao)
    except met_repo.METNotAvailable:
        return {"error": "No meteorological data available"}, 409

    return {
        'end_timestamp': int(end_time_datetime.timestamp())
    }, 200


def _load_runway_prediction_template(result: dict = None):
    destination_airports = airports_api.get_destination_airports()

    return f.render_template('runway.html',
                             result=result,
                             destination_airports=destination_airports)


def _load_runway_prediction_template_with_warning(message: str):
    f.flash(message, category="warning")
    return _load_runway_prediction_template()


def _load_runway_config_prediction_template(result: dict = None):
    destination_airports = airports_api.get_destination_airports()

    return f.render_template('runwayConfig.html',
                             result=result,
                             destination_airports=destination_airports)


def _load_runway_config_prediction_template_with_warning(message: str):
    f.flash(message, category="warning")
    return _load_runway_config_prediction_template()