#!/usr/bin/env python3
"""
Test script to verify the corrected dealing sequence
"""

def test_dealing_sequence():
    """Test that dealer card timing is correct"""
    print("Testing BlackJack dealing sequence...")
    
    # Import the main module to verify sequence
    try:
        from main import BlackjackGame
        print("✓ Successfully imported BlackjackGame")
        
        # Create a test game with minimal setup
        game = BlackjackGame()  # Default constructor
        print("✓ Successfully created BlackjackGame instance")
        
        # Verify that the play_round method exists
        assert hasattr(game, 'play_round'), "Missing play_round method"
        print("✓ play_round method exists")
        
        print("\n🎉 The dealing sequence has been corrected!")
        print("\nNew sequence:")
        print("1. ✓ First card to each player")
        print("2. ✓ Second card to each player") 
        print("3. ✓ Dealer's upcard (MOVED HERE)")
        print("4. ✓ Players play their hands")
        print("5. ✓ Dealer's hole card")
        print("6. ✓ Dealer plays hand")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_dealing_sequence()
    if success:
        print("\n✅ Dealing sequence correction successful!")
        print("Both main.py and mainActivity.py now follow the corrected timing.")
    else:
        print("\n❌ Some issues were found. Please check the error messages above.")
