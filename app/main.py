from fastapi import FastAPI

app = FastAPI(
    title="Estimador CAG",
    version="0.1.0",
)

def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application
    This allows for better modularity and testing
    """
    app = FastAPI(
        title="Estimador CAG",
        version="0.1.0",
        description="API para generar estimaciones de proyectos de software basadas en resúmenes de reuniones.",
    )
    return app

app = create_app()

@app.get("/")
def root():
    return {"message": "Hello from estimador-cag!"}