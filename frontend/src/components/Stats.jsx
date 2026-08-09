import React from 'react'

function Stats({ stats }) {
  if (!stats) {
    return (
      <div className="text-center py-12 bg-white rounded-lg shadow">
        <p className="text-gray-500">No statistics available.</p>
      </div>
    )
  }

  const formatCurrency = (value) => {
    if (!value) return '₹0'
    return `₹${value.toLocaleString('en-IN')}`
  }

  const categoryColors = {
    'enterprise_rfp': 'bg-purple-500',
    'smb_enquiry': 'bg-blue-500',
    'marketing': 'bg-pink-500',
    'alliances': 'bg-indigo-500',
    'finance': 'bg-green-500',
    'triage': 'bg-gray-500',
  }

  const assigneeColors = {
    'u_aarti': 'bg-red-500',
    'u_rohit': 'bg-blue-500',
    'u_meera': 'bg-pink-500',
    'u_karan': 'bg-purple-500',
    'u_divya': 'bg-green-500',
    'u_triage': 'bg-gray-500',
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold text-gray-900 mb-6">Statistics</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-sm">Total Tasks</p>
          <p className="text-3xl font-bold text-gray-900">{stats.total_tasks}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-sm">Total Deal Value</p>
          <p className="text-3xl font-bold text-gray-900">{formatCurrency(stats.total_deal_value_inr)}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-sm">Average Confidence</p>
          <p className="text-3xl font-bold text-gray-900">{(stats.average_confidence * 100).toFixed(0)}%</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-sm">Categories</p>
          <p className="text-3xl font-bold text-gray-900">{Object.keys(stats.by_category).length}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">By Category</h3>
          <div className="space-y-3">
            {Object.entries(stats.by_category).map(([category, count]) => (
              <div key={category} className="flex items-center">
                <div className="flex-1">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">{category}</span>
                    <span className="text-sm text-gray-500">{count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`${categoryColors[category] || 'bg-gray-500'} h-2 rounded-full`}
                      style={{ width: `${(count / stats.total_tasks) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">By Assignee</h3>
          <div className="space-y-3">
            {Object.entries(stats.by_assignee).map(([assignee, count]) => (
              <div key={assignee} className="flex items-center">
                <div className="flex-1">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">{assignee}</span>
                    <span className="text-sm text-gray-500">{count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`${assigneeColors[assignee] || 'bg-gray-500'} h-2 rounded-full`}
                      style={{ width: `${(count / stats.total_tasks) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">By Priority</h3>
          <div className="space-y-3">
            {Object.entries(stats.by_priority).map(([priority, count]) => (
              <div key={priority} className="flex items-center">
                <div className="flex-1">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700 capitalize">{priority}</span>
                    <span className="text-sm text-gray-500">{count}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`${
                        priority === 'high' ? 'bg-red-500' :
                        priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                      } h-2 rounded-full`}
                      style={{ width: `${(count / stats.total_tasks) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Stats
