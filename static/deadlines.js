// This runs once for every row in the table.
//   row          the table row (<tr>)
//   cell         the deadline cell (<td>)
//   opportunity  the row's data, including days_left from the server
function showDeadline(row, cell, opportunity) {
  const rawText = cell.textContent || "";
  cell.textContent = "";

  const wrap = document.createElement("div");
  wrap.className = "deadline-wrap";

  const dateText = document.createElement("span");
  dateText.className = "deadline-date";
  dateText.textContent = rawText;
  wrap.appendChild(dateText);

  const label = buildDeadlineLabel(opportunity.days_left);
  if (label) {
    const labelText = document.createElement("span");
    labelText.className = "deadline-label " + label.className;
    labelText.textContent = label.text;
    wrap.appendChild(labelText);
  }

  cell.appendChild(wrap);
}

function buildDeadlineLabel(daysLeft) {
  if (typeof daysLeft !== "number") {
    return null;
  }

  if (daysLeft < 0) {
    return { text: "Overdue", className: "deadline-overdue" };
  }

  if (daysLeft === 0) {
    return { text: "due today", className: "deadline-today" };
  }

  if (daysLeft <= 7) {
    const days = daysLeft === 1 ? "day" : "days";
    return { text: "Due in " + daysLeft + " " + days, className: "deadline-soon" };
  }

  return null;
}
