import { useState } from 'react'
import { SymptomForm } from './components/SymptomForm'
import { ResponseCard } from './components/ResponseCard'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/v1/agent/respond'

export function App() {
  const [symptoms, setSymptoms] = useState('')
  const [context, setContext] = useState({})
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: 'frontend-session',
          user_input: symptoms,
          context,
        }),
      })
      if (!response.ok) throw new Error('API request failed')
      setData(await response.json())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main>
      <h1>Health AI Agent MVP</h1>
      <p className="disclaimer">Informational support only — not a substitute for medical care.</p>
      <SymptomForm
        value={symptoms}
        onChange={setSymptoms}
        context={context}
        onContextChange={(k, v) => setContext((old) => ({ ...old, [k]: v }))}
        onSubmit={onSubmit}
        loading={loading}
      />
      {error && <p className="error">{error}</p>}
      <ResponseCard data={data} />
    </main>
  )
}
