// n8n "Code" node (Run Once for All Items).
// Turns the list of low-stock products from the SQL step into one Telegram message.
const lines = $input.all().map(item =>
  `• ${item.json.product}: ${item.json.available} left`
);

return [{
  json: {
    message: `⚠️ Low Stock Alert — Padel Shop\n\n${lines.join('\n')}\n\nTime to reorder! 📦`
  }
}];
