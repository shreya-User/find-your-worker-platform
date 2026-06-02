# from flask import Blueprint, request, jsonify, redirect, url_for
# from voice_assistant import process_command, speak_to_audio_data

# voice_bp = Blueprint('voice', __name__)

# @voice_bp.route('/command', methods=['POST'])
# def handle_voice_command():
#     data = request.json
#     command = data.get('command')

#     if not command:
#         return jsonify({"error": "No command provided"}), 400

#     action = process_command(command)

#     if action["type"] == "redirect":
#         # For redirection, we'll send the URL back to the frontend
#         # The frontend JavaScript will handle the actual redirection
#         return jsonify(action)
#     elif action["type"] == "speak":
#         # For speaking, we'll send the message back to the frontend
#         # The frontend JavaScript will handle playing the audio
#         return jsonify(action)
#     elif action["type"] == "speak_and_logout":
#         # For logout, we'll send the message back to the frontend
#         # The frontend JavaScript will handle playing the audio and then triggering logout
#         return jsonify(action)
    
#     return jsonify(action)

# @voice_bp.route('/speak', methods=['POST'])
# def get_speech_audio():
#     data = request.json
#     text = data.get('text')

#     if not text:
#         return jsonify({"error": "No text provided"}), 400
    
#     audio_data = speak_to_audio_data(text)
#     if audio_data:
#         return jsonify({"audio": audio_data})
#     else:
#         return jsonify({"error": "Failed to generate speech audio"}), 500

from flask import Blueprint, request, jsonify
import logging

voice_bp = Blueprint('voice', __name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@voice_bp.route('/command', methods=['POST'])
def handle_voice_command():
    try:
        # Log the incoming request
        logger.debug(f"Received request: {request.json}")
        
        data = request.json
        if not data:
            logger.error("No JSON data received")
            return jsonify({"error": "No data provided"}), 400
        
        command = data.get('command')
        
        if not command:
            logger.error("No command in request")
            return jsonify({"error": "No command provided"}), 400
        
        logger.info(f"Processing command: {command}")
        
        # Import here to avoid circular imports
        from voice_assistant import process_command
        action = process_command(command)
        
        logger.debug(f"Action result: {action}")
        return jsonify(action)
    
    except Exception as e:
        logger.error(f"Error in handle_voice_command: {e}")
        return jsonify({"error": str(e)}), 500


@voice_bp.route('/speak', methods=['POST'])
def get_speech_audio():
    try:
        logger.debug(f"Received speak request: {request.json}")
        
        data = request.json
        if not data:
            logger.error("No JSON data received for speak")
            return jsonify({"error": "No data provided"}), 400
        
        text = data.get('text')
        
        if not text:
            logger.error("No text provided for speak")
            return jsonify({"error": "No text provided"}), 400
        
        logger.info(f"Generating speech for: {text}")
        
        # Import here to avoid circular imports
        from voice_assistant import speak_to_audio_data
        audio_data = speak_to_audio_data(text)
        
        if audio_data:
            logger.debug("Audio generated successfully")
            return jsonify({"audio": audio_data})
        else:
            logger.error("Failed to generate audio")
            return jsonify({"error": "Failed to generate speech audio"}), 500
    
    except Exception as e:
        logger.error(f"Error in get_speech_audio: {e}")
        return jsonify({"error": str(e)}), 500