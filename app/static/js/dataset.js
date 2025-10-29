import { renderTable } from "./tables.js";

const tableOrder = [
    "mdl_user",
    "mdl_course",
    "mdl_resource",
    "mdl_course_categories",
    "tag",
    "category_tag",
    "course_tag",
    "resource_tag",
    "mdl_context",
    "mdl_role_assignments",
    "mdl_role"
];

document.getElementById("dataset-form").addEventListener("submit", function(e) {
    e.preventDefault();
    const btn = document.getElementById("dataset-form").querySelector("button");
    btn.disabled = true;

    const n_utenti = document.getElementById("n_utenti").value;
    const n_corsi = document.getElementById("n_corsi").value;
    const n_risorse = document.getElementById("n_risorse").value;

    const url = `/api/dataset/generate?n_utenti=${n_utenti}&n_corsi=${n_corsi}&n_risorse=${n_risorse}`;
    const evtSource = new EventSource(url);

    evtSource.onerror = function(err) {
        console.error("SSE error", err);
        evtSource.close();
        document.getElementById("status").innerText = "Errore nella connessione SSE";
        btn.disabled = false;
    };

    evtSource.onmessage = function(event) {
        const data = JSON.parse(event.data);

        const bar = document.getElementById("progress-bar");
        bar.style.width = data.progress + "%";
        bar.innerText = data.progress + "%";
        document.getElementById("status").innerText = data.message;

        if (data.progress === 100) {
            let navHtml = `<div class="container"><div class="row justify-content-center g-2" id="tableTabs" role="tablist">`;
            let contentHtml = `<div class="tab-content mt-3" id="tableTabsContent">`;

            tableOrder.forEach((name, idx) => {
                const records = data.result[name];
                if (!records) return;

                const activeClass = idx === 0 ? "active" : "";
                const showActive = idx === 0 ? "show active" : "";
                const selected = idx === 0 ? "true" : "false";

                navHtml += `
                    <div class="col-6 col-md-4 col-lg-2 text-center">
                        <button class="btn btn-outline-primary w-100 ${activeClass}" id="${name}-tab"
                                data-bs-toggle="tab" data-bs-target="#${name}-pane"
                                type="button" role="tab" aria-controls="${name}-pane"
                                aria-selected="${selected}">
                                ${name}
                        </button>
                    </div>
                `;

                contentHtml += `
                    <div class="tab-pane fade ${showActive}" id="${name}-pane" 
                         role="tabpanel" aria-labelledby="${name}-tab">
                        ${renderTable(name, records)}
                    </div>
                `;
            });

            navHtml += `</div></div>`;
            contentHtml += `</div>`;

            const downloadBtn = `
                <div class="text-center mt-4">
                    <a href="/api/dataset/download_all" class="btn btn-lg btn-success">
                        Scarica tutte le tabelle (ZIP)
                    </a>
                </div>
            `;

            document.getElementById("tables-container").innerHTML = navHtml + contentHtml + downloadBtn;

            evtSource.close();
            btn.disabled = false;
        }
    };
});