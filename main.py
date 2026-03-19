import cv2 as cv
import threading
import os
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

system_state = {
    "status": "idle",
    "current_video": None,
    "video_to_play": None
}

@app.route('/play', methods=['POST'])
def play():
    video_id = request.args.get('video_id')
    video_path = f"videos/{video_id}.mp4"

    if not os.path.exists(video_path):
        return jsonify({"error": f"Video file {video_id}.mp4 not found"}), 404

    if system_state["status"] == "playing" or system_state["video_to_play"] is not None:
        return jsonify({"error": "Already playing a video"}), 400
    system_state["video_to_play"] = video_path

    return jsonify({"message": f"Started playing {video_id}"}), 200


@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": system_state["status"],
        "current_video": system_state["current_video"]
    }), 200


def run_flask():
    app.run(port=5000, debug=False, use_reloader=False)


if __name__ == '__main__':
    if not os.path.exists('videos'):
        os.makedirs('videos')

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    print("API server ON http://127.0.0.1:5000")
    print("Waiting for commands: (Press CTRL+C to exit)")

    while True:
        try:
            if system_state["video_to_play"] is not None:
                video_path = system_state["video_to_play"]
                system_state["status"] = "playing"
                system_state["current_video"] = video_path
                system_state["video_to_play"] = None
                cap = cv.VideoCapture(video_path)

                if not cap.isOpened():
                    system_state["status"] = "error"
                    system_state["current_video"] = None
                    continue

                while cap.isOpened():
                    ret, frame = cap.read()

                    if not ret:
                        break
                    cv.imshow('Vision Simulator', frame)

                    if cv.waitKey(30) & 0xFF == ord('q'):
                        break

                cap.release()
                cv.destroyAllWindows()
                system_state["status"] = "idle"
                system_state["current_video"] = None
            else:
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\nEnd of the program.")
            break