import sys
from app.api.estimate.services import estimate_from_transcript

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/estimate_example.py 'transcripción de la reunión'")
        sys.exit(1)

    transcript = sys.argv[1]
    print("Enviando transcripción a LLM...\n")
    estimation = estimate_from_transcript(transcript)
    print("\n=== ESTIMACIÓN GENERADA ===\n")
    print(estimation)
