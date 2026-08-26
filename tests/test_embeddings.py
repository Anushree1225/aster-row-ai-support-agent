from app.rag.embeddings import embed_text


if __name__ == "__main__":
    vector = embed_text(
        "Customers can return standard-plan items within 30 calendar days of delivery."
    )

    print("Embedding generated successfully!")
    print("Dimensions:", len(vector))
    print("First 5 values:", vector[:5])