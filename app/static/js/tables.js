export function renderTable(title, records) {
    if (!records || records.length === 0) return "";

    const headers = Object.keys(records[0]);
    let html = `<h3 class="mt-4">${title}</h3>`;
    html += `<div class="table-responsive"><table class="table table-bordered table-hover table-sm align-middle">`;
    html += `<thead class="table-dark"><tr>`;
    headers.forEach(h => { html += `<th scope="col">${h}</th>`; });
    html += `</tr></thead><tbody>`;

    records.forEach(row => {
        html += "<tr>";
        headers.forEach(h => { html += `<td>${row[h] ?? ""}</td>`; });
        html += "</tr>";
    });

    html += "</tbody></table></div>";
    return html;
}