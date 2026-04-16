
from ai_engine_manager import AIEngineManager


def test_expert():
    engine = AIEngineManager(mode="fast")

    # Test text from a hypothetical incident
    sinhala_test = "2024.04.10 දින රාත්‍රී 10.30 ට පමණ අලුත්ගම පොලිස් වසමේදී නිවසක් බිඳ රුපියල් 500,000 ක රන් භාණ්ඩ සොරාගෙන ඇත."

    print("\n--- Testing Expert AI Pipeline ---")
    print(f"Input: {sinhala_test}")

    # We use restricted_list=["ollama"] to ensure it uses the local/kaggle expert model
    # or just call_ai normally to see the best result.
    response = engine.call_ai(
        sinhala_test,
        system_prompt="You are a Super-Expert Sri Lanka Police translator. Convert this to institutional standard English.",
        timeout=60
    )

    print("\n--- AI Response ---")
    print(response)

    if "{" in response:
        print("\n✅ Verification Success: AI returned formatted data.")
    else:
        print("\n⚠️ Verification Partial: AI returned narrative (check for institutional tone).")

if __name__ == "__main__":
    test_expert()
