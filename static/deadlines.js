// This runs once for every row in the table.
//   row          the table row (<tr>)
//   cell         the deadline cell (<td>)
//   opportunity  the row's data, including days_left from the server
//
// Labels go by days_left only, whatever the status (see AGENTS.md).
function showDeadline(row, cell, opportunity) {
  const days = opportunity.days_left;
  let text = "";
  let colour = "";

  if (days < 0) {
    text = "Overdue";
    colour = "deadline-overdue";
  } else if (days === 0) {
    text = "Due today";
    colour = "deadline-soon";
  } else if (days <= 7) {
    text = "Due in " + days + (days === 1 ? " day" : " days");
    colour = "deadline-soon";
  } else {
    return;
  }

  const label = document.createElement("span");
  label.className = "deadline-label " + colour;
  label.textContent = text;
  cell.appendChild(label);
}
