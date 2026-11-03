// This runs once for every row in the table.
//   row          the table row (<tr>)
//   cell         the deadline cell (<td>)
//   opportunity  the row's data, including days_left from the server
function showDeadline(row, cell, opportunity) {
  // Finished rows need no deadline warning: just show the date.
  const finished = ["Submitted", "Successful", "Unsuccessful"];
  if (finished.includes(opportunity.status)) {
    return;
  }

  const daysLeft = opportunity.days_left;

  if (daysLeft < 0) {
    row.classList.add("deadline-overdue");
    cell.textContent = "Overdue";
    return;
  }

  if (daysLeft === 0) {
    row.classList.add("deadline-today");
    cell.textContent = "Due today";
    return;
  }

  if (daysLeft <= 7) {
    row.classList.add("deadline-soon");
    cell.textContent = `Due in ${daysLeft} day${daysLeft === 1 ? "" : "s"}`;
  }
}
