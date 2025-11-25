// Sample data for Regional Industrial Analysis Dashboard

const industrialData = {
    // Key Performance Indicators
    kpis: {
        totalProduction: 2847500,
        activeFacilities: 156,
        employmentRate: 87.3,
        energyEfficiency: 92.1
    },

    // Regional production data
    regionalProduction: {
        labels: ['North Region', 'South Region', 'East Region', 'West Region', 'Central Region'],
        data: [650000, 720000, 580000, 490000, 407500],
        colors: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
    },

    // Industrial growth trends (last 12 months)
    growthTrends: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [
            {
                label: 'Manufacturing',
                data: [2.1, 2.4, 2.8, 3.2, 3.5, 3.8, 4.1, 4.3, 4.6, 4.8, 5.0, 5.2],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                fill: true
            },
            {
                label: 'Technology',
                data: [1.8, 2.2, 2.6, 3.1, 3.4, 3.9, 4.2, 4.5, 4.9, 5.1, 5.4, 5.7],
                borderColor: '#764ba2',
                backgroundColor: 'rgba(118, 75, 162, 0.1)',
                fill: true
            },
            {
                label: 'Energy',
                data: [1.5, 1.7, 2.0, 2.3, 2.5, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0],
                borderColor: '#f5576c',
                backgroundColor: 'rgba(245, 87, 108, 0.1)',
                fill: true
            }
        ]
    },

    // Detailed regional data for the table
    regionalDetails: [
        {
            region: 'North Region',
            production: '650,000',
            facilities: 42,
            employment: '89.2%',
            growthRate: '+5.8%'
        },
        {
            region: 'South Region',
            production: '720,000',
            facilities: 38,
            employment: '91.5%',
            growthRate: '+6.2%'
        },
        {
            region: 'East Region',
            production: '580,000',
            facilities: 35,
            employment: '85.7%',
            growthRate: '+4.9%'
        },
        {
            region: 'West Region',
            production: '490,000',
            facilities: 28,
            employment: '82.3%',
            growthRate: '+3.7%'
        },
        {
            region: 'Central Region',
            production: '407,500',
            facilities: 13,
            employment: '88.1%',
            growthRate: '+4.4%'
        }
    ],

    // Monthly data for trend analysis
    monthlyMetrics: [
        { month: 'Jan 2024', production: 2650000, facilities: 148, employment: 85.1, efficiency: 89.3 },
        { month: 'Feb 2024', production: 2698000, facilities: 150, employment: 85.8, efficiency: 89.8 },
        { month: 'Mar 2024', production: 2732000, facilities: 151, employment: 86.2, efficiency: 90.2 },
        { month: 'Apr 2024', production: 2765000, facilities: 152, employment: 86.5, efficiency: 90.6 },
        { month: 'May 2024', production: 2798000, facilities: 153, employment: 86.9, efficiency: 91.1 },
        { month: 'Jun 2024', production: 2821000, facilities: 154, employment: 87.1, efficiency: 91.5 },
        { month: 'Jul 2024', production: 2835000, facilities: 155, employment: 87.2, efficiency: 91.8 },
        { month: 'Aug 2024', production: 2841000, facilities: 155, employment: 87.3, efficiency: 92.0 },
        { month: 'Sep 2024', production: 2845000, facilities: 156, employment: 87.3, efficiency: 92.1 },
        { month: 'Oct 2024', production: 2847500, facilities: 156, employment: 87.3, efficiency: 92.1 }
    ],

    // Sector breakdown data
    sectorData: {
        manufacturing: {
            percentage: 42.3,
            value: 1204352,
            facilities: 66,
            employment: 45200
        },
        technology: {
            percentage: 28.7,
            value: 817233,
            facilities: 44,
            employment: 32100
        },
        energy: {
            percentage: 18.9,
            value: 538178,
            facilities: 28,
            employment: 18900
        },
        agriculture: {
            percentage: 10.1,
            value: 287598,
            facilities: 18,
            employment: 12400
        }
    }
};

// Export for use in other modules (if using ES6 modules)
// export default industrialData;

// Make data available globally for the dashboard
window.industrialData = industrialData;