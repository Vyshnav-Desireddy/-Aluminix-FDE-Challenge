import React, { useState } from 'react'
import { api } from '../api'

function IngestEmail({ onIngested }) {
  const [formData, setFormData] = useState({
    email_id: '',
    thread_id: '',
    from_name: '',
    from_email: '',
    to: '',
    subject: '',
    body: '',
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await api.ingestEmail(formData)
      setResult(response)
      if (onIngested) {
        onIngested(response)
      }
      // Clear form on success
      setFormData({
        email_id: '',
        thread_id: '',
        from_name: '',
        from_email: '',
        to: '',
        subject: '',
        body: '',
      })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'created': return 'bg-green-100 text-green-800 border-green-200'
      case 'ignored': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'duplicate': return 'bg-blue-100 text-blue-800 border-blue-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold text-gray-900 mb-6">Ingest Email</h2>

      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email ID *
              </label>
              <input
                type="text"
                name="email_id"
                value={formData.email_id}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="em_001"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Thread ID *
              </label>
              <input
                type="text"
                name="thread_id"
                value={formData.thread_id}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="th_001"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                From Name *
              </label>
              <input
                type="text"
                name="from_name"
                value={formData.from_name}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="John Smith"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                From Email *
              </label>
              <input
                type="email"
                name="from_email"
                value={formData.from_email}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="john@example.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              To *
            </label>
            <input
              type="email"
              name="to"
              value={formData.to}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="sales@aluminix.com"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subject *
            </label>
            <input
              type="text"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="RFP for Enterprise DMS"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Body *
            </label>
            <textarea
              name="body"
              value={formData.body}
              onChange={handleChange}
              required
              rows={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Email body content..."
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing...' : 'Ingest Email'}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {result && (
          <div className={`mt-4 p-4 border rounded-md ${getStatusColor(result.status)}`}>
            <h3 className="font-semibold mb-2 capitalize">
              Status: {result.status}
            </h3>
            {result.status === 'created' && result.task && (
              <div className="text-sm">
                <p>Task created successfully!</p>
                <p className="mt-1">Task ID: {result.task.task_id}</p>
                <p>Assignee: {result.task.assignee_id}</p>
                <p>Category: {result.task.category}</p>
              </div>
            )}
            {result.status === 'ignored' && result.classification && (
              <div className="text-sm">
                <p>Email classified as non-task (ignored)</p>
                <p className="mt-1">Reason: {result.classification.reason}</p>
              </div>
            )}
            {result.status === 'duplicate' && result.task && (
              <div className="text-sm">
                <p>Email already processed (duplicate)</p>
                <p className="mt-1">Existing Task ID: {result.task.task_id}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default IngestEmail
