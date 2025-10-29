import json, asyncio, io, zipfile
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from app.core.dataset_manager import genera_dataset_steps

router = APIRouter()

@router.get("/generate")
async def generate_dataset(n_utenti: int, n_corsi: int, n_risorse: int, request: Request):
    async def event_generator():
        for step in genera_dataset_steps(n_utenti, n_corsi, n_risorse, request):
            yield {"event": "message", "data": json.dumps(step)}
            if step.get("progress") == 100:
                return
            
            await asyncio.sleep(0.1)
    
    return EventSourceResponse(event_generator())



@router.get("/download_all")
def download_all_tables(request: Request):
    dfs = getattr(request.app.state, "last_dfs", None)
    if not dfs:
        raise HTTPException(status_code=404, detail="Nessun dataset generato ancora")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for name, df in dfs.items():
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            zip_file.writestr(f"{name}.csv", csv_buffer.getvalue())

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=dataset.zip"}
    )