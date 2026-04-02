document.addEventListener('DOMContentLoaded', () => {
    
    let lastMtime = 0;
    const ordersTbody = document.getElementById('orders-tbody');
    const summaryTbody = document.getElementById('summary-tbody');
    const statusIndicator = document.getElementById('update-status');

    // Function to render the orders table
    const renderOrders = (data) => {
        if (!data || data.length === 0) {
            ordersTbody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No data available.</td></tr>';
            return;
        }

        ordersTbody.innerHTML = data.map(item => `
            <tr>
                <td>${item.order_id || 'N/A'}</td>
                <td>${item.customer_id || 'N/A'}</td>
                <td>${item.customer_name || 'N/A'}</td>
                <td>${item.region || 'N/A'}</td>
                <td>${item.amount !== null ? item.amount + ' ' + (item.currency || '') : 'N/A'}</td>
                <td class="amount-col">¥${parseFloat(item.amount_cny).toFixed(2)}</td>
            </tr>
        `).join('');
    };

    // Function to render the summary table
    const renderSummary = (data) => {
        if (!data || data.length === 0) {
            summaryTbody.innerHTML = '<tr><td colspan="2" style="text-align:center;">No data available.</td></tr>';
            return;
        }

        summaryTbody.innerHTML = data.map(item => `
            <tr>
                <td>${item.region || 'N/A'}</td>
                <td class="amount-col">¥${parseFloat(item.average_amount_cny).toFixed(2)}</td>
            </tr>
        `).join('');
    };

    // Main fetch data function
    const fetchLatestData = async () => {
        try {
            const res = await fetch('/api/data');
            const data = await res.json();
            
            if (data.error) {
                console.error("Error fetching data:", data.error);
                return;
            }

            renderOrders(data.merged_data);
            renderSummary(data.region_summary);
            
            // Briefly flutter the live indicator to show a refresh happened
            statusIndicator.classList.remove('show');
            setTimeout(() => statusIndicator.classList.add('show'), 150);

        } catch (err) {
            console.error("Failed to parse data payload", err);
        }
    };

    // Polling function
    const pollForUpdates = async () => {
        try {
            const res = await fetch('/api/status');
            const statusData = await res.json();
            
            if (statusData.mtime !== lastMtime) {
                console.log(`Update detected. Old mtime: ${lastMtime}, New mtime: ${statusData.mtime}`);
                lastMtime = statusData.mtime;
                await fetchLatestData();
            }
        } catch (err) {
            console.error("Failed to check status", err);
        }
    };

    // Initial setup
    statusIndicator.classList.add('show');
    
    // Check for updates immediately, then poll every 2 seconds
    pollForUpdates();
    setInterval(pollForUpdates, 2000);

});
