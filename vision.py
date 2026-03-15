"""
Vision Module for KARMA AI
Handles face recognition and computer vision features

Features:
- Face enrollment for authorized users
- Face verification on startup
- Security login system
- Photo capture capabilities
"""

import os
import logging
from datetime import datetime
import json
from pathlib import Path

# Try to import cv2, make it optional
try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    cv2 = None
    np = None


class Vision:
    """
    Vision system for KARMA AI
    Handles face recognition and security features
    """
    
    def __init__(self, data_dir=None):
        """Initialize vision module"""
        self.logger = logging.getLogger('KARMA-Vision')
        
        # Data directory
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), 'data', 'faces')
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Users file
        self.users_file = self.data_dir.parent / 'authorized_users.json'
        self.authorized_users = self._load_users()
        
        # Face recognizer
        self.face_recognizer = None
        self.face_cascade = None
        self._initialize_cv()
        
        # Recognition settings
        self.recognition_threshold = 70  # Confidence threshold (0-100)
        
        self.logger.info("Vision module initialized")
    
    def _initialize_cv(self):
        """Initialize OpenCV components"""
        if not HAS_CV2:
            self.logger.warning("OpenCV (cv2) not installed. Vision features disabled.")
            return
        
        try:
            # Load face cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                self.logger.warning("Could not load face cascade")
            
            # Try to load or create face recognizer
            try:
                self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
                self.logger.info("Face recognizer initialized (LBPH)")
            except:
                try:
                    self.face_recognizer = cv2.face.EigenFaceRecognizer_create()
                    self.logger.info("Face recognizer initialized (Eigen)")
                except:
                    self.logger.warning("Could not create face recognizer")
            
            self.logger.info("OpenCV initialized successfully")
            
        except Exception as e:
            self.logger.error(f"OpenCV initialization error: {e}")
    
    def _load_users(self):
        """Load authorized users from file"""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading users: {e}")
        return {}
    
    def _save_users(self):
        """Save authorized users to file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.authorized_users, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving users: {e}")
            return False
    
    def enroll_face(self, user_name, num_samples=20):
        """
        Enroll a new user's face
        
        Args:
            user_name: Name of the user
            num_samples: Number of face samples to collect
            
        Returns:
            True if enrollment successful
        """
        self.logger.info(f"Starting face enrollment for: {user_name}")
        
        # Create user directory
        user_dir = self.data_dir / user_name.lower().replace(' ', '_')
        user_dir.mkdir(exist_ok=True)
        
        # Initialize camera
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            self.logger.error("Cannot access camera")
            return False
        
        samples = []
        count = 0
        required_samples = num_samples
        
        self.logger.info(f"Please look at the camera. Collecting {required_samples} samples...")
        
        while count < required_samples:
            ret, frame = cap.read()
            
            if not ret:
                self.logger.error("Failed to capture frame")
                break
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )
            
            for (x, y, w, h) in faces:
                # Draw rectangle around face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Save face sample
                face_roi = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face_resized, (200, 200))
                
                # Save image
                img_path = user_dir / f"img_{count}.jpg"
                cv2.imwrite(str(img_path), face_resized)
                
                samples.append(face_resized)
                count += 1
                
                # Show progress
                cv2.putText(
                    frame,
                    f"Sample {count}/{required_samples}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )
            
            # Show frame
            cv2.imshow('KARMA - Face Enrollment', frame)
            
            # Press 'q' to quit early
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if count >= num_samples // 2:  # At least half the samples
            # Add user to authorized list
            self.authorized_users[user_name.lower()] = {
                'name': user_name,
                'samples': count,
                'enrolled_at': datetime.now().isoformat()
            }
            self._save_users()
            
            # Train recognizer
            self._train_recognizer()
            
            self.logger.info(f"Face enrollment complete for {user_name}")
            return True
        
        self.logger.error("Face enrollment failed - not enough samples")
        return False
    
    def _train_recognizer(self):
        """Train face recognizer with enrolled users"""
        if not self.face_recognizer:
            return False
        
        faces = []
        labels = []
        
        label_map = {}
        current_label = 0
        
        for user_folder in self.data_dir.iterdir():
            if user_folder.is_dir():
                user_name = user_folder.name
                label_map[user_name] = current_label
                
                for img_path in user_folder.glob("*.jpg"):
                    try:
                        img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
                        if img is not None:
                            faces.append(img)
                            labels.append(current_label)
                    except:
                        pass
                
                current_label += 1
        
        if faces:
            try:
                self.face_recognizer.train(faces, np.array(labels))
                self.logger.info(f"Face recognizer trained with {len(faces)} samples")
                return True
            except Exception as e:
                self.logger.error(f"Training error: {e}")
        
        return False
    
    def verify_face(self, timeout=10):
        """
        Verify face for login
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            (success, user_name) tuple
        """
        if not self.face_recognizer or not self.authorized_users:
            self.logger.warning("Face recognition not configured")
            return True, "Guest"  # Allow access if not configured
        
        self.logger.info("Starting face verification...")
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            self.logger.error("Cannot access camera")
            return True, "Guest"
        
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )
            
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                face_resized = cv2.resize(face_roi, (200, 200))
                
                try:
                    label, confidence = self.face_recognizer.predict(face_resized)
                    
                    # Draw rectangle
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Check confidence (lower is better)
                    if confidence < (100 - self.recognition_threshold):
                        # Find user name
                        user_names = list(self.authorized_users.keys())
                        if label < len(user_names):
                            user_name = self.authorized_users[user_names[label]]['name']
                            
                            cap.release()
                            cv2.destroyAllWindows()
                            
                            self.logger.info(f"Face verified: {user_name}")
                            return True, user_name
                    
                    cv2.putText(
                        frame,
                        f"Confidence: {int(confidence)}",
                        (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        1
                    )
                    
                except Exception as e:
                    self.logger.error(f"Recognition error: {e}")
            
            # Show frame
            cv2.putText(
                frame,
                "Looking for authorized face...",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )
            
            cv2.imshow('KARMA - Face Verification', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        self.logger.warning("Face verification timeout")
        return False, None
    
    def login(self, require_face=True):
        """
        Perform login process
        
        Args:
            require_face: Whether to require face verification
            
        Returns:
            (success, user_name) tuple
        """
        if not require_face:
            return True, "User"
        
        success, user = self.verify_face(timeout=15)
        
        if success:
            return True, user
        
        # Allow fallback
        return True, "Guest"
    
    def get_authorized_users(self):
        """Get list of authorized users"""
        return list(self.authorized_users.values())
    
    def remove_user(self, user_name):
        """Remove a user from authorized list"""
        user_key = user_name.lower()
        
        if user_key in self.authorized_users:
            del self.authorized_users[user_key]
            self._save_users()
            
            # Remove user folder
            user_dir = self.data_dir / user_key
            if user_dir.exists():
                import shutil
                shutil.rmtree(user_dir)
            
            # Retrain
            self._train_recognizer()
            
            return True
        
        return False
    
    def take_photo(self, filename=None):
        """Take a photo using the default camera"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            self.logger.error("Cannot access camera")
            return None
        
        ret, frame = cap.read()
        cap.release()
        cv2.destroyAllWindows()
        
        if ret:
            if not filename:
                filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            
            cv2.imwrite(filename, frame)
            self.logger.info(f"Photo saved: {filename}")
            return filename
        
        return None
    
    def detect_faces(self):
        """Detect and return faces in frame (for preview)"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return None
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5
            )
            return len(faces)
        
        return 0
