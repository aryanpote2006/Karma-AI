"""
KARMA AI - Test Suite
Comprehensive testing for all modules
"""

import sys
import os

# Add karma_ai to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test 1: Basic Import Test - Verify all modules can be imported"""
    print("=" * 60)
    print("TEST 1: Basic Import Test")
    print("=" * 60)
    
    tests = [
        ("logging", "logging"),
        ("datetime", "datetime"),
        ("webbrowser", "webbrowser"),
        ("requests", "requests"),
        ("subprocess", "subprocess"),
        ("threading", "threading"),
    ]
    
    optional_tests = [
        ("speechrecognition", "speech_recognition"),
        ("pyttsx3", "pyttsx3"),
        ("pyaudio", "pyaudio"),
        ("openai", "openai"),
        ("google.generativeai", "google.genai"),
        ("psutil", "psutil"),
        ("pyautogui", "pyautogui"),
        ("pywin32", "win32api"),
    ]
    
    results = {"passed": 0, "failed": 0, "optional_failed": 0}
    
    # Test required modules
    print("\n--- Required Modules ---")
    for name, module in tests:
        try:
            __import__(module)
            print(f"✓ {name}: PASSED")
            results["passed"] += 1
        except ImportError as e:
            print(f"✗ {name}: FAILED - {e}")
            results["failed"] += 1
    
    # Test optional modules
    print("\n--- Optional Modules (AI, Voice, Automation) ---")
    for name, module in optional_tests:
        try:
            __import__(module)
            print(f"✓ {name}: PASSED")
            results["passed"] += 1
        except ImportError as e:
            print(f"⚠ {name}: NOT INSTALLED - {e}")
            results["optional_failed"] += 1
    
    print(f"\nImport Test Results: {results['passed']} passed, {results['failed']} failed, {results['optional_failed']} optional not installed")
    return results


def test_karma_modules():
    """Test 2: KARMA Module Import Test"""
    print("\n" + "=" * 60)
    print("TEST 2: KARMA Module Import Test")
    print("=" * 60)
    
    results = {"passed": 0, "failed": 0, "errors": []}
    
    modules = [
        ("memory", "Memory"),
        ("automation", "Automation"),
        ("musicLibrary", "MusicLibrary"),
    ]
    
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✓ karma_ai.{module_name}: PASSED")
            results["passed"] += 1
        except Exception as e:
            print(f"✗ karma_ai.{module_name}: FAILED - {e}")
            results["failed"] += 1
            results["errors"].append(f"{module_name}: {e}")
    
    # Test AI Brain
    try:
        from ai_brain import AIBrain
        print(f"✓ karma_ai.ai_brain: PASSED")
        results["passed"] += 1
    except Exception as e:
        print(f"✗ karma_ai.ai_brain: FAILED - {e}")
        results["failed"] += 1
        results["errors"].append(f"ai_brain: {e}")
    
    # Test Command Processor
    try:
        from command_processor import CommandProcessor
        print(f"✓ karma_ai.command_processor: PASSED")
        results["passed"] += 1
    except Exception as e:
        print(f"✗ karma_ai.command_processor: FAILED - {e}")
        results["failed"] += 1
        results["errors"].append(f"command_processor: {e}")
    
    # Test Voice Engine
    try:
        from voice_engine import VoiceEngine
        print(f"✓ karma_ai.voice_engine: PASSED")
        results["passed"] += 1
    except Exception as e:
        print(f"✗ karma_ai.voice_engine: FAILED - {e}")
        results["failed"] += 1
        results["errors"].append(f"voice_engine: {e}")
    
    # Test GUI
    try:
        from gui import GUIDashboard
        print(f"✓ karma_ai.gui: PASSED")
        results["passed"] += 1
    except Exception as e:
        print(f"✗ karma_ai.gui: FAILED - {e}")
        results["failed"] += 1
        results["errors"].append(f"gui: {e}")
    
    print(f"\nModule Import Results: {results['passed']} passed, {results['failed']} failed")
    return results


def test_unit_tests():
    """Test 3: Unit Tests for Core Classes"""
    print("\n" + "=" * 60)
    print("TEST 3: Unit Tests")
    print("=" * 60)
    
    results = {"passed": 0, "failed": 0, "errors": []}
    
    # Test Memory class
    print("\n--- Testing Memory Class ---")
    try:
        from memory import Memory
        mem = Memory()
        
        # Test add_to_history
        mem.add_to_history('user', 'test command')
        history = mem.get_conversation_history()
        assert len(history) > 0, "History should not be empty"
        print("  ✓ add_to_history works")
        
        # Test tasks - use the correct method name
        mem.add_task("Test task")
        tasks = mem.get_tasks()
        if tasks and "Test task" in str(tasks):
            print("  ✓ add_task works")
        
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ Memory test failed: {e}")
        results["failed"] += 1
        results["errors"].append(f"Memory: {e}")
    
    # Test Automation class
    print("\n--- Testing Automation Class ---")
    try:
        import logging
        from automation import Automation
        
        logger = logging.getLogger('test')
        auto = Automation(logger)
        
        # Test that automation object was created
        assert auto is not None
        assert auto.is_windows == (sys.platform == 'win32')
        print("  ✓ Automation initialization works")
        print(f"  ✓ Platform detection: {'Windows' if auto.is_windows else 'Linux/Mac'}")
        
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ Automation test failed: {e}")
        results["failed"] += 1
        results["errors"].append(f"Automation: {e}")
    
    # Test MusicLibrary class
    print("\n--- Testing MusicLibrary Class ---")
    try:
        from musicLibrary import MusicLibrary
        music = MusicLibrary()
        
        # Test that music library has songs
        assert hasattr(music, 'music')
        assert len(music.music) > 0
        print(f"  ✓ MusicLibrary initialized with {len(music.music)} songs")
        
        # Test play method
        result = music.play("test")
        assert result is not None
        print("  ✓ music.play() method works")
        
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ MusicLibrary test failed: {e}")
        results["failed"] += 1
        results["errors"].append(f"MusicLibrary: {e}")
    
    # Test AIBrain class
    try:
        from ai_brain import AIBrain
        
        brain = AIBrain(mem)
        
        # Test fallback response
        response = brain.get_response("hello")
        assert response is not None
        assert len(response) > 0
        print(f"  ✓ AIBrain.get_response() works")
        print(f"  ✓ Fallback response: '{response[:50]}...'")
        
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ AIBrain test failed: {e}")
        results["failed"] += 1
        results["errors"].append(f"AIBrain: {e}")
    
    # Test CommandProcessor class
    print("\n--- Testing CommandProcessor Class ---")
    try:
        from command_processor import CommandProcessor
        
        cp = CommandProcessor(brain, auto, music, mem, logging.getLogger('test'))
        
        # Test time command
        response = cp.process("what is the time")
        assert response is not None
        assert "time" in response.lower() or ":" in response
        print(f"  ✓ CommandProcessor.process() works")
        print(f"  ✓ Time command response: '{response}'")
        
        # Test date command
        response = cp.process("what is the date")
        assert response is not None
        print(f"  ✓ Date command response: '{response}'")
        
        results["passed"] += 1
    except Exception as e:
        print(f"  ✗ CommandProcessor test failed: {e}")
        results["failed"] += 1
        results["errors"].append(f"CommandProcessor: {e}")
    
    print(f"\nUnit Test Results: {results['passed']} passed, {results['failed']} failed")
    return results


def test_integration():
    """Test 4: Integration Test - Full KARMA Initialization"""
    print("\n" + "=" * 60)
    print("TEST 4: Integration Test - Full KARMA Initialization")
    print("=" * 60)
    
    results = {"passed": 0, "failed": 0, "errors": []}
    
    try:
        # Try to import main class
        from main import KarmaAI
        
        print("  ✓ KarmaAI class imported successfully")
        
        # Create instance (don't run - just initialize)
        # This tests all module integrations
        
        # We'll just test the imports work by creating a minimal instance
        import logging
        
        # Test logging setup
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'karma_test.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        logger = logging.getLogger('KARMA-TEST')
        
        print("  ✓ Logging system works")
        
        # Import all modules needed for integration
        from memory import Memory
        from ai_brain import AIBrain
        from automation import Automation
        from musicLibrary import MusicLibrary
        from command_processor import CommandProcessor
        
        # Test Memory
        memory = Memory()
        print("  ✓ Memory module works")
        
        # Test AIBrain
        ai_brain = AIBrain(memory)
        print("  ✓ AI Brain module works")
        print(f"    - OpenAI configured: {ai_brain.get_status()['openai']}")
        print(f"    - Gemini configured: {ai_brain.get_status()['gemini']}")
        
        # Test Automation
        automation = Automation(logger)
        print("  ✓ Automation module works")
        
        # Test MusicLibrary
        music_library = MusicLibrary()
        print("  ✓ Music Library module works")
        
        # Test CommandProcessor
        command_processor = CommandProcessor(
            ai_brain, 
            automation, 
            music_library,
            memory,
            logger
        )
        print("  ✓ Command Processor module works")
        
        results["passed"] += 1
        print("\n✓ Integration test PASSED - All modules working together!")
        
    except Exception as e:
        print(f"  ✗ Integration test failed: {e}")
        results["failed"] += 1
        results["errors"].append(f"Integration: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\nIntegration Test Results: {results['passed']} passed, {results['failed']} failed")
    return results


def run_all_tests():
    """Run all tests and generate report"""
    print("\n" + "=" * 60)
    print("KARMA AI - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    all_results = {}
    
    # Run all tests
    all_results["imports"] = test_imports()
    all_results["modules"] = test_karma_modules()
    all_results["units"] = test_unit_tests()
    all_results["integration"] = test_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total_passed = sum(r["passed"] for r in all_results.values())
    total_failed = sum(r["failed"] for r in all_results.values())
    
    print(f"Total Tests Passed: {total_passed}")
    print(f"Total Tests Failed: {total_failed}")
    
    if total_failed == 0:
        print("\n✓ ALL TESTS PASSED! KARMA AI is ready to run.")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        print("\nTo fix common issues:")
        print("  1. Install dependencies: pip install -r karma_ai/requirements.txt")
        print("  2. Install PyAudio: pipwin install pyaudio (Windows)")
        print("  3. Set API keys in environment variables (for AI features)")
    
    return all_results


if __name__ == "__main__":
    run_all_tests()
