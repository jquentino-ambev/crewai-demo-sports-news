import { useEffect, useState } from 'react'

const apiUrl = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

function errorMessage(response, body) {
  if (typeof body?.detail === 'string') return body.detail
  return `A API não conseguiu gerar o relatório (${response.status}).`
}

function App() {
  const [tema, setTema] = useState('')
  const [reportHtml, setReportHtml] = useState('')
  const [error, setError] = useState('')
  const [running, setRunning] = useState(false)
  const [startedAt, setStartedAt] = useState()
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    if (!running) return undefined
    const timer = window.setInterval(() => setElapsed(Math.floor((Date.now() - startedAt) / 1000)), 1000)
    return () => window.clearInterval(timer)
  }, [running, startedAt])

  async function generate(event) {
    event.preventDefault()
    const topic = tema.trim()
    if (!topic) return

    setRunning(true)
    setError('')
    setStartedAt(Date.now())
    setElapsed(0)
    try {
      const response = await fetch(`${apiUrl}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tema: topic }),
      })
      const body = await response.json().catch(() => null)
      if (!response.ok || !body?.report_html) throw new Error(errorMessage(response, body))
      setReportHtml(body.report_html)
    } catch (requestError) {
      setError(requestError.message || 'Não foi possível comunicar com a API. Tente novamente.')
    } finally {
      setRunning(false)
    }
  }

  function download() {
    const url = URL.createObjectURL(new Blob([reportHtml], { type: 'text/html;charset=utf-8' }))
    const link = document.createElement('a')
    link.href = url
    link.download = 'report.html'
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <main>
      <header>
        <h1>Sports Journal Crew</h1>
        <p>Pesquise notícias esportivas e receba o relatório em HTML.</p>
      </header>

      <form onSubmit={generate} className="panel">
        <label htmlFor="tema">Tema</label>
        <div className="form-row">
          <input id="tema" value={tema} onChange={(event) => setTema(event.target.value)} placeholder="Ex.: futebol brasileiro" required disabled={running} />
          <button type="submit" disabled={running}>{running ? 'Gerando…' : 'Gerar relatório'}</button>
        </div>
        {running && <p className="status" role="status">A crew está trabalhando. Tempo decorrido: {elapsed}s.</p>}
        {error && <p className="error" role="alert">{error}</p>}
      </form>

      {reportHtml && <section className="report">
        <div className="report-header">
          <h2>Prévia do relatório</h2>
          <button type="button" onClick={download}>Baixar report.html</button>
        </div>
        <iframe title="Prévia do relatório" srcDoc={reportHtml} sandbox="" />
      </section>}
    </main>
  )
}

export default App
