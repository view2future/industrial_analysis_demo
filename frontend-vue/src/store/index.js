import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isLoggedIn: false,
    token: localStorage.getItem('token') || null
  }),

  actions: {
    login(userData, token) {
      this.user = userData
      this.isLoggedIn = true
      this.token = token
      localStorage.setItem('token', token)
      localStorage.setItem('isLoggedIn', 'true')
    },

    logout() {
      this.user = null
      this.isLoggedIn = false
      this.token = null
      localStorage.removeItem('token')
      localStorage.removeItem('isLoggedIn')
    },

    updateUser(userData) {
      this.user = { ...this.user, ...userData }
    }
  }
})

export const useReportStore = defineStore('report', {
  state: () => ({
    reports: [],
    currentReport: null,
    loading: false
  }),

  actions: {
    setReports(reports) {
      this.reports = reports
    },

    setCurrentReport(report) {
      this.currentReport = report
    },

    setLoading(status) {
      this.loading = status
    },

    addReport(report) {
      this.reports.unshift(report)
    },

    updateReport(reportId, updatedData) {
      const index = this.reports.findIndex(report => report.id === reportId)
      if (index !== -1) {
        this.reports[index] = { ...this.reports[index], ...updatedData }
      }
    }
  }
})