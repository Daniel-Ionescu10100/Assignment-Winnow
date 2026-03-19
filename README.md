# Winnow Vision - Automated Video Playback Prototype

This repo contains a method to automate Winnow Vision testing via programmatic video playback. This service replaces the human effort of replacing physical 3D-printed food replicas under the camera by allowing an automated test runner to trigger waste events on display.

---

# Design Description

I followed a client-server microservices architecture, built using Python. It consists of two scripts to separate the control service from the testing logic:

### 1) Video Playback Control Service - `main.py`

A local web service that runs a Flask API in a background thread to listen for commands, while using OpenCV in the main thread to render the video. I chose OpenCV because I've worked with it in the past and it is really easy to use for controlling the display window without unpredictable behavior.

### 2) Automated Test Runner - `test_runner.py`

A mock automation script that simulates regression testing. It discovers video files in the selected folder, triggers them in successive order, and polls the system state.

---

# Proposed Interface / API

The service exposes a simple RESTful HTTP API:

* **POST /play?video_id=<name>**
  Triggers the playback of a specific scenario. For example, `?video_id=apple` looks for `videos/apple.mp4`.

* **GET /status**
  Returns the current state of the player as a JSON object (e.g., `{"status": "playing", "current_video": "videos/apple.mp4"}`).

By wrapping the OpenCV video player in an HTTP API, the testing framework can easily organize tests. A test script queries `/status` to ensure the system is ready, sends a `/play` command, and waits for the state to return to idle. Then it can assert whether the Vision system correctly identifies the item.

---

# Design Considerations

The prototype was built with the following practical aspects in mind:

* **Repeated requests:**
  If a test accidentally triggers playback while a video is already running, the API defensively catches this and returns an HTTP 400 Bad Request (`{"error": "Already playing a video"}`).

* **System state:**
  Tests can reliably determine if the system is idle, playing, or has encountered an error by making a GET request to the `/status` endpoint.

* **Video selection:**
  The test specifies the exact scenario dynamically via the `video_id` URL query parameter.

* **Error handling:**
  If a requested video file does not exist, the API returns an HTTP 404 Not Found without attempting to open the player. If the file exists but OpenCV fails to read it, the system state is updated to `error`.

* **Test repeatability:**
  Once a video finishes (or is manually skipped via the `q` key), the system cleanly releases the file, destroys the window, and resets its state to idle. The included `test_runner.py` successfully demonstrates this by reliably running multiple videos back-to-back.

---

# Run Instructions and Notes

## Dependencies

This prototype requires Python 3.x and the following libraries:

```
pip install flask opencv-python requests
```

## Starting the Video Playback Service (`main.py`)

1. Create a directory named `videos` in the root folder.
2. Place your test `.mp4` files inside the `videos` directory.
3. Start the service using the command appropriate for your operating system:

* **Windows:**
  `python main.py`

* **macOS / Linux:**
  `python3 main.py`

The server will start on `http://127.0.0.1:5000` and wait for commands.

## Running the Test Runner

In a new terminal window, execute the test runner to sequentially play all videos found in the `videos` folder:

* **Windows:**
  `python test_runner.py`

* **macOS / Linux:**
  `python3 test_runner.py`

---

# Assumptions & Limitations

* **File format:**
  The system currently assumes test videos are standard `.mp4` files stored locally in the `videos/` directory relative to the script.

* **In-memory state:**
  The system state is kept in the application's memory. If the server restarts, the state resets entirely.

---

# Improvements

* **A `/stop` endpoint:**
  To allow automated tests to abort playback mid-way if a test fails early, saving execution time.

* **Programmatic pause and resume capabilities:**
  This would allow automated tests to pause the video on a specific frame to give the Vision model more time to process the waste event.
