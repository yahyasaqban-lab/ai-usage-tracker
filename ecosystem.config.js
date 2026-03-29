// PM2 Configuration for AI Usage Tracker
module.exports = {
  apps: [
    {
      name: 'ai-tracker-api',
      script: 'ai-tracker-api.py',
      interpreter: 'python3',
      cwd: '/home/y7/.openclaw/workspace/ai-usage-tracker',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/api-error.log',
      out_file: './logs/api-out.log',
      log_file: './logs/api-combined.log',
      time: true
    },
    {
      name: 'ai-tracker-auto',
      script: 'openclaw-usage-integration.py',
      args: '--auto-track --interval 60',
      interpreter: 'python3',
      cwd: '/home/y7/.openclaw/workspace/ai-usage-tracker',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/auto-error.log',
      out_file: './logs/auto-out.log',
      log_file: './logs/auto-combined.log',
      time: true
    },
    {
      name: 'ai-tracker-dashboard',
      script: '/usr/bin/python3',
      args: '-m http.server 8002',
      cwd: '/home/y7/.openclaw/workspace/ai-usage-tracker',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/dashboard-error.log',
      out_file: './logs/dashboard-out.log',
      log_file: './logs/dashboard-combined.log',
      time: true
    }
  ]
};