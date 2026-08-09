import React from 'react'

function TaskList({ tasks, onRefresh }) {
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getCategoryColor = (category) => {
    const colors = {
      'enterprise_rfp': 'bg-purple-100 text-purple-800',
      'smb_enquiry': 'bg-blue-100 text-blue-800',
      'marketing': 'bg-pink-100 text-pink-800',
      'alliances': 'bg-indigo-100 text-indigo-800',
      'finance': 'bg-green-100 text-green-800',
      'triage': 'bg-gray-100 text-gray-800',
    }
    return colors[category] || 'bg-gray-100 text-gray-800'
  }

  const formatCurrency = (value) => {
    if (!value) return 'N/A'
    return `₹${value.toLocaleString('en-IN')}`
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold text-gray-900">Tasks</h2>
        <button
          onClick={onRefresh}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
        >
          Refresh
        </button>
      </div>

      {tasks.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">No tasks found. Ingest an email to get started.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map((task) => (
            <div key={task.task_id} className="bg-white rounded-lg shadow p-6 hover:shadow-md transition">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{task.title}</h3>
                <div className="flex space-x-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded ${getPriorityColor(task.priority)}`}>
                    {task.priority}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded ${getCategoryColor(task.category)}`}>
                    {task.category}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Assignee</p>
                  <p className="font-medium text-gray-900">{task.assignee_id}</p>
                </div>
                <div>
                  <p className="text-gray-500">Company</p>
                  <p className="font-medium text-gray-900">{task.company_name || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-500">Deal Value</p>
                  <p className="font-medium text-gray-900">{formatCurrency(task.deal_value_inr)}</p>
                </div>
                <div>
                  <p className="text-gray-500">Deadline</p>
                  <p className="font-medium text-gray-900">{task.due_date || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-500">Confidence</p>
                  <p className="font-medium text-gray-900">{(task.confidence * 100).toFixed(0)}%</p>
                </div>
                <div>
                  <p className="text-gray-500">Created</p>
                  <p className="font-medium text-gray-900">
                    {new Date(task.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>

              {task.description && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-gray-600 text-sm">{task.description}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default TaskList
