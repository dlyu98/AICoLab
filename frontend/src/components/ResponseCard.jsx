export function ResponseCard({ data }) {
  if (!data) return null

  const r = data.response
  return (
    <section className="panel">
      <h2>AI Guidance</h2>
      <p><strong>Summary:</strong> {r.summary}</p>
      <p><strong>Urgency:</strong> <span className="badge">{r.urgency_level}</span></p>
      <p><strong>Answer:</strong> {r.user_friendly_answer}</p>
      <List title="Possible considerations" items={r.possible_considerations} />
      <List title="Follow-up questions" items={r.follow_up_questions} />
      <List title="Self-care guidance" items={r.self_care_guidance} />
      <List title="When to seek care" items={r.when_to_seek_care} />
      <List title="Red flags detected" items={r.red_flags_detected} />
      <p className="disclaimer">{r.disclaimer}</p>
    </section>
  )
}

function List({ title, items }) {
  if (!items?.length) return null
  return (
    <div>
      <h3>{title}</h3>
      <ul>{items.map((item, idx) => <li key={`${title}-${idx}`}>{item}</li>)}</ul>
    </div>
  )
}
