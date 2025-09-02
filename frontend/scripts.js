// Larvae Feeding & Facility Section JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Track form submission states to prevent multiple submissions
    const formSubmissionStates = new Map();
    
    // Form elements
    const forms = {
        // Waste Management
        wasteSourcing: document.getElementById('wasteSourcingForm'),
        storageRecords: document.getElementById('storageRecordsForm'),
        processingRecords: document.getElementById('processingRecordsForm'),
        wasteEnvironmentalMonitoring: document.getElementById('wasteEnvironmentalMonitoringForm'),
        // Feeding
        feedingRecords: document.getElementById('feedingRecordsForm'),
        feedingEnvironmentalMonitoring: document.getElementById('environmentalMonitoringForm'),
        substratePreparation: document.getElementById('substratePreparationForm'),
        healthIntervention: document.getElementById('healthInterventionForm'),
        harvestYield: document.getElementById('harvestYieldForm'),
        feedingSchedule: document.getElementById('feedingScheduleForm'),
        // Facility
        cageMonitoring: document.getElementById('cageMonitoringForm'),
        facilityMaintenance: document.getElementById('facilityMaintenanceForm'),
        pupaeTransition: document.getElementById('pupaeTransitionForm'),
        eggCollection: document.getElementById('eggCollectionForm'),
        baitPreparation: document.getElementById('baitPreparationForm')
    };

    // API endpoints
    const apiEndpoints = {
        'wasteSourcing': 'waste-sourcing',
        'storageRecords': 'storage-records',
        'processingRecords': 'processing-records',
        // Environmental Monitoring Endpoints
        'wasteEnvironmentalMonitoring': 'environmental-monitoring-waste',
        'feedingEnvironmentalMonitoring': 'feeding/environmental-monitoring',
        'batchInfo': 'hatchery/batch',
        'feedingRecords': 'hatchery/feeding',
        'hatcheryMonitoring': 'hatchery/monitoring',
        'hatcheryCleaning': 'hatchery/cleaning',
        'hatcheryProblems': 'hatchery/problems',
        'cageMonitoring': 'facility/cage-monitoring',
        'facilityMaintenance': 'facility/maintenance',
        'pupaeTransition': 'facility/pupae-transition',
        'eggCollection': 'facility/egg-collection',
        'baitPreparation': 'facility/bait-preparation',
        'healthIntervention': 'feeding/health-intervention',
        'harvestYield': 'feeding/harvest-yield',
        'feedingSchedule': 'feeding/schedule'
    };

    // Notification function
    function showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = 'alert'; // reset
        notification.classList.add(type === 'success' ? 'alert-success' : 'alert-danger');
        notification.style.display = 'block';
        setTimeout(() => {
            notification.style.display = 'none';
        }, 4000);
    }

    // Validate substrate batch ID exists
    async function validateSubstrateBatchId(batchId) {
        try {
            const response = await fetch(`/api/substrate/batches/${batchId}`, { credentials: 'include' });
            if (!response.ok) {
                throw new Error('Substrate batch ID not found');
            }
            return true;
        } catch (error) {
            console.error('Error validating substrate batch ID:', error);
            return false;
        }
    }

    // Form validation
    async function validateForm(form, formType) {
        console.log(`Validating form: ${formType}`);
        const errors = {};
        const formData = new FormData(form);
        
        console.log('Form fields:', Array.from(formData.entries()));
        
        form.querySelectorAll('[required]').forEach(field => {
            if (!field.value.trim()) {
                errors[field.name] = `${field.name.replace(/([A-Z])/g, ' $1').trim()} is required`;
                field.classList.add('is-invalid');
                console.log(`Missing required field: ${field.name}`);
            } else {
                field.classList.remove('is-invalid');
            }
        });

        // Form-specific validation (can be expanded)
        switch(formType) {
            case 'feedingEnvironmentalMonitoring':
                const temp = parseFloat(formData.get('temperature'));
                if (isNaN(temp)) {
                    errors.temperature = 'Temperature is required';
                }
                const humidity = parseFloat(formData.get('humidity'));
                if (isNaN(humidity)) {
                    errors.humidity = 'Humidity is required';
                }
                break;
            // Add other specific validations if needed
        }

        return Object.keys(errors).length > 0 ? errors : null;
    }

    // Handle form submission
    async function handleSubmit(form, formType) {
        // Prevent multiple submissions
        if (formSubmissionStates.get(formType)) {
            console.log(`Form ${formType} is already being submitted, ignoring duplicate submission`);
            return;
        }
        
        console.log(`Handling submission for form: ${formType}`);
        
        // Set submission flag
        formSubmissionStates.set(formType, true);
        
        // Disable submit button to prevent multiple clicks
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton ? submitButton.innerHTML : '';
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
        }
        
        try {
            const errors = await validateForm(form, formType);
            if (errors) {
                Object.entries(errors).forEach(([field, message]) => {
                    const input = form.querySelector(`[name="${field}"]`);
                    if (input) {
                        input.classList.add('is-invalid');
                        const feedback = input.nextElementSibling;
                        if (feedback && feedback.classList.contains('invalid-feedback')) {
                            feedback.textContent = message;
                        }
                    }
                });
                // This is a placeholder for a real alert function
                console.error('Please fix the errors in the form', errors);
                return;
            }

            const formData = new FormData(form);
            const data = {};
            
            const numericFields = [
                'feed_quantity_kg', 'larvae_age_days', 'larvae_weight_g', 'consumption_rate_percent',
                'temperature', 'humidity', 'moisture_percentage', 'larvae_collected_kg', 'storage_temp',
                'start_weight', 'end_weight', 'consumption',
                'lighting_hours', 'pupae_weight_added', 'old_pupae_removed', 'number_of_crates', 'eggs_collected'
            ];

            formData.forEach((value, key) => {
                if (numericFields.includes(key)) {
                    data[key] = value ? parseFloat(value) : null;
                } else {
                    data[key] = value;
                }
            });

            const endpoint = apiEndpoints[formType];
            if (!endpoint) {
                throw new Error(`No API endpoint defined for form type: ${formType}`);
            }

            const apiUrl = `/api/${endpoint}`;
            console.log('Sending data to:', apiUrl);
            console.log('Data:', data);

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
                credentials: 'include'
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || `HTTP error! status: ${response.status}`);
            }
            
            console.log('Response data:', result);
            showNotification(result.message || 'Data submitted successfully!', 'success');
            form.reset();
        } catch (error) {
            console.error('Error details:', error);
            showNotification(`Error: ${error.message}`, 'error');
        } finally {
            // Reset submission flag and re-enable button
            formSubmissionStates.set(formType, false);
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            }
        }
    }

    // Add event listeners to forms (only once)
    Object.entries(forms).forEach(([formType, form]) => {
        if (form) {
            console.log(`Adding event listeners to form: ${formType}`);
            
            // Check if event listeners are already added
            if (form.hasAttribute('data-event-listeners-added')) {
                console.log(`Event listeners already added to form: ${formType}`);
                return;
            }
            
            // Mark form as having event listeners
            form.setAttribute('data-event-listeners-added', 'true');
            
            form.querySelectorAll('input, select, textarea').forEach(input => {
                input.addEventListener('input', function() {
                    this.classList.remove('is-invalid');
                });
            });

            form.addEventListener('submit', function(e) {
                if(formType === 'feedingEnvironmentalMonitoring') {
                    console.log('Environmental Monitoring form submit event fired');
                }
                e.preventDefault();
                console.log(`Form submitted: ${formType}`);
                handleSubmit(this, formType);
            });
        } else {
            // It's normal for some forms not to be on every page, so this is a soft warning.
            // console.warn(`Form not found: ${formType}`);
        }
    });

    // Handle records filtering
    const recordsFilterForm = document.getElementById('recordsFilterForm');
    if (recordsFilterForm) {
        recordsFilterForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const date = document.getElementById('recordDate').value;
            const section = document.getElementById('recordSection').value;
            const resultsContainer = document.getElementById('recordsResults');
            
            if (!date) {
                showNotification('Please select a date.', 'error');
                return;
            }

            resultsContainer.innerHTML = `
                <div class="loading">
                    <i class="fas fa-spinner"></i>
                    <p>Loading records...</p>
                </div>`;

            try {
                const response = await fetch(`/api/records?date=${date}&section=${section}`, { credentials: 'include' });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || 'Failed to fetch records');
                }

                const data = await response.json();
                
                if (data.success) {
                    displayRecords(data.records);
                } else {
                    throw new Error(data.message || 'An unknown error occurred');
                }

            } catch (error) {
                console.error('Error fetching records:', error);
                resultsContainer.innerHTML = `<p class="text-danger">Error: ${error.message}</p>`;
                showNotification(error.message, 'error');
            }
        });
    }

    function displayRecords(records) {
        const resultsContainer = document.getElementById('recordsResults');
        resultsContainer.innerHTML = '';

        if (Object.keys(records).length === 0) {
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <h4>No Records Found</h4>
                    <p>No records found for the selected date and section.</p>
                </div>`;
            return;
        }

        for (const [tableName, tableRecords] of Object.entries(records)) {
            const tableWrapper = document.createElement('div');
            tableWrapper.className = 'record-table-wrapper';

            const tableTitle = document.createElement('h3');
            tableTitle.textContent = tableName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            tableWrapper.appendChild(tableTitle);

            // Create responsive table container
            const tableContainer = document.createElement('div');
            tableContainer.className = 'table-responsive';

            const table = document.createElement('table');
            table.className = 'table table-striped table-bordered';

            // Create table header
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            const headers = Object.keys(tableRecords[0]);
            
            headers.forEach(headerText => {
                const th = document.createElement('th');
                th.textContent = headerText.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                headerRow.appendChild(th);
            });
            thead.appendChild(headerRow);
            table.appendChild(thead);

            // Create table body
            const tbody = document.createElement('tbody');
            tableRecords.forEach(record => {
                const row = document.createElement('tr');
                headers.forEach(header => {
                    const cell = document.createElement('td');
                    const value = record[header];
                    
                    // Format the cell content based on data type
                    if (value === null || value === undefined) {
                        cell.textContent = 'N/A';
                        cell.style.color = '#6c757d';
                        cell.style.fontStyle = 'italic';
                    } else {
                        // Format dates
                        if (header.toLowerCase().includes('date') || header.toLowerCase().includes('time')) {
                            cell.className = 'date-cell';
                            if (typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}/)) {
                                const date = new Date(value);
                                cell.textContent = date.toLocaleDateString();
                            } else {
                                cell.textContent = value;
                            }
                        }
                        // Format numbers
                        else if (header.toLowerCase().includes('weight') || 
                                 header.toLowerCase().includes('quantity') || 
                                 header.toLowerCase().includes('amount') ||
                                 header.toLowerCase().includes('temperature') ||
                                 header.toLowerCase().includes('humidity') ||
                                 header.toLowerCase().includes('percentage')) {
                            cell.className = 'number-cell';
                            const numValue = parseFloat(value);
                            if (!isNaN(numValue)) {
                                cell.textContent = numValue.toLocaleString();
                            } else {
                                cell.textContent = value;
                            }
                        }
                        // Format status/boolean values
                        else if (typeof value === 'boolean' || 
                                 (typeof value === 'string' && ['yes', 'no', 'true', 'false'].includes(value.toLowerCase()))) {
                            const statusBadge = document.createElement('span');
                            statusBadge.className = 'status-badge';
                            
                            if (value === true || value === 'yes' || value === 'true') {
                                statusBadge.classList.add('success');
                                statusBadge.textContent = 'Yes';
                            } else if (value === false || value === 'no' || value === 'false') {
                                statusBadge.classList.add('danger');
                                statusBadge.textContent = 'No';
                            } else {
                                statusBadge.classList.add('info');
                                statusBadge.textContent = value;
                            }
                            
                            cell.appendChild(statusBadge);
                        }
                        // Handle long text
                        else if (typeof value === 'string' && value.length > 50) {
                            const truncatedText = document.createElement('span');
                            truncatedText.className = 'text-truncate';
                            truncatedText.title = value; // Show full text on hover
                            truncatedText.textContent = value.length > 100 ? value.substring(0, 100) + '...' : value;
                            cell.appendChild(truncatedText);
                        }
                        // Default formatting
                        else {
                            cell.textContent = value;
                        }
                    }
                    
                    // Add data-label for mobile responsiveness
                    cell.setAttribute('data-label', header.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()));
                    
                    row.appendChild(cell);
                });
                tbody.appendChild(row);
            });
            table.appendChild(tbody);
            tableContainer.appendChild(table);
            tableWrapper.appendChild(tableContainer);
            resultsContainer.appendChild(tableWrapper);
        }
    }

    // --- Harvest Efficiency Analysis ---
    const analyzeBtn = document.getElementById('analyzeHarvestEfficiencyBtn');
    const chartCanvas = document.getElementById('harvestEfficiencyChart');
    let efficiencyChart = null; 

    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', async (event) => {
            event.preventDefault();
            console.log('Analysis started...');
            
            const chartContainer = chartCanvas.parentElement;
            chartContainer.innerHTML = '<p class="text-info">Loading analysis...</p>';
            if (efficiencyChart) {
                efficiencyChart.destroy();
                efficiencyChart = null;
                chartContainer.innerHTML = '<canvas id="harvestEfficiencyChart"></canvas>';
            }

            try {
                console.log('Fetching efficiency data from /api/statistics/harvest-efficiency...');
                const response = await fetch('/api/statistics/harvest-efficiency', { credentials: 'include' });
                console.log('Fetch response received:', response);

                if (!response.ok) {
                    console.error('Fetch response not OK. Status:', response.status);
                    const errorData = await response.json();
                    throw new Error(errorData.message || `Server error: ${response.status}`);
                }

                console.log('Parsing JSON data...');
                const data = await response.json();
                console.log('Data parsed successfully:', data);

                if (data.error) {
                    console.error('Application error from server:', data.error);
                    throw new Error(data.error);
                }
                
                chartContainer.innerHTML = '<canvas id="harvestEfficiencyChart"></canvas>';

                if (data.length === 0) {
                    chartContainer.innerHTML = '<p class="text-muted">No harvest data available to analyze.</p>';
                    console.log('No data to display. Ending process.');
                    return;
                }
                
                try {
                    console.log('Attempting to render efficiency chart...');
                    renderEfficiencyChart(data);
                    console.log('Chart rendered successfully.');

                    console.log('Attempting to display efficiency comparison table...');
                    displayEfficiencyComparisonTable(data);
                    console.log('Comparison table displayed successfully.');

                } catch (chartError) {
                    console.error("Chart rendering failed:", chartError);
                    if(chartContainer) {
                        chartContainer.innerHTML = `<p class="text-danger">Could not display chart: ${chartError.message}</p>`;
                    }
                }

            } catch (error) {
                console.error('Error in analysis process:', error);
                chartContainer.innerHTML = `<p class="text-danger">Error: ${error.message}</p>`;
                showNotification(error.message, 'error');
            }
        });
    }

    function displayEfficiencyComparisonTable(data) {
        const tableContainer = document.getElementById('efficiencyComparisonTable');
        if (!tableContainer) return;

        tableContainer.innerHTML = ''; // Clear previous table

        const table = document.createElement('table');
        table.className = 'table table-bordered table-hover text-center';

        table.innerHTML = `
            <thead class="table-light">
                <tr>
                    <th>Batch ID</th>
                    <th>Harvest Date</th>
                    <th>Actual Ratio</th>
                    <th>Target Ratio</th>
                    <th>Efficiency</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
            </tbody>
        `;

        const tbody = table.querySelector('tbody');
        
        [...data].reverse().forEach(item => { // Show most recent first
            const efficiency = item.efficiency_percentage;
            const isEfficient = efficiency >= 100;
            const rowClass = isEfficient ? 'table-success' : 'table-danger';

            const row = document.createElement('tr');
            row.className = rowClass;

            row.innerHTML = `
                <td>${item.batch_id}</td>
                <td>${new Date(item.date).toLocaleDateString()}</td>
                <td><strong>${item.actual_ratio}</strong></td>
                <td>${item.target_ratio}</td>
                <td>${efficiency.toFixed(2)}%</td>
                <td><strong>${isEfficient ? 'Efficient' : 'Inefficient'}</strong></td>
            `;
            tbody.appendChild(row);
        });

        tableContainer.appendChild(table);
    }

    function renderEfficiencyChart(data) {
        if (efficiencyChart) {
            efficiencyChart.destroy();
        }
        
        const chartCanvas = document.getElementById('harvestEfficiencyChart');
        if (!chartCanvas) return;

        const labels = data.map(item => `Batch ${item.batch_id}`);
        const efficiencyValues = data.map(item => item.efficiency_percentage);

        const chartData = {
            labels: labels,
            datasets: [{
                label: 'Batch Harvest Efficiency (%)',
                data: efficiencyValues,
                fill: true,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                tension: 0.4,
                pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointRadius: 5,
                pointHoverRadius: 7
            }, {
                label: 'Target Efficiency',
                data: Array(data.length).fill(100),
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 2,
                borderDash: [5, 5],
                pointRadius: 0,
                fill: false
            }]
        };

        const config = {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Efficiency (%)' }
                    },
                    x: {
                        title: { display: true, text: 'Batch' }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                if (context.dataset.label.includes('Target')) {
                                    return 'Target: 100%';
                                }
                                const index = context.dataIndex;
                                const item = data[index];
                                return [
                                    `Efficiency: ${context.parsed.y.toFixed(2)}%`,
                                    `Actual Ratio: ${item.actual_ratio}`,
                                    `Date: ${new Date(item.date).toLocaleDateString()}`
                                ];
                            }
                        }
                    }
                }
            }
        };
        
        efficiencyChart = new Chart(chartCanvas, config);
    }

    // --- Customers, Sales, Deliveries, Feedback Section Logic ---
    const customerForm = document.getElementById('customerForm');
    const customerTableBody = document.querySelector('#customerTable tbody');
    const salesForm = document.getElementById('salesForm');
    const salesTableBody = document.querySelector('#salesTable tbody');
    const saleCustomerSelect = document.getElementById('saleCustomer');
    const deliveryForm = document.getElementById('deliveryForm');
    const deliveryTableBody = document.querySelector('#deliveryTable tbody');
    const deliveryCustomerSelect = document.getElementById('deliveryCustomer');
    const feedbackForm = document.getElementById('feedbackForm');
    const feedbackTableBody = document.querySelector('#feedbackTable tbody');
    const feedbackCustomerSelect = document.getElementById('feedbackCustomer');

    let customers = [];
    let sales = [];
    let deliveries = [];
    let feedbacks = [];

    // Fetch customers from backend and update all dropdowns
    async function fetchCustomers() {
      const res = await fetch('/api/customers');
      customers = await res.json();
      updateCustomerDropdowns();
      renderCustomers();
    }
    function updateCustomerDropdowns() {
      const options = '<option value="">Select customer</option>' + customers.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
      if (saleCustomerSelect) saleCustomerSelect.innerHTML = options;
      if (deliveryCustomerSelect) deliveryCustomerSelect.innerHTML = options;
      if (feedbackCustomerSelect) feedbackCustomerSelect.innerHTML = options;
    }

    // Fetch and render sales
    async function fetchSales() {
      const res = await fetch('/api/sales');
      sales = await res.json();
      renderSales();
    }
    // Fetch and render deliveries
    async function fetchDeliveries() {
      const res = await fetch('/api/deliveries');
      deliveries = await res.json();
      renderDeliveries();
    }
    // Fetch and render feedback
    async function fetchFeedback() {
      const res = await fetch('/api/feedback');
      feedbacks = await res.json();
      renderFeedback();
    }

    // Render functions
    function renderCustomers() {
      if (!customerTableBody) return;
      customerTableBody.innerHTML = '';
      customers.forEach(c => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${c.name}</td><td>${c.contact || ''}</td><td>${c.email || ''}</td><td>${c.address || ''}</td><td><button class='btn btn-sm btn-warning' onclick='editCustomer(${c.id})'>Edit</button></td>`;
        customerTableBody.appendChild(row);
      });
    }
    function renderSales() {
      if (!salesTableBody) return;
      salesTableBody.innerHTML = '';
      sales.forEach(s => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${s.date}</td><td>${s.customer_name}</td><td>${s.product || ''}</td><td>${s.quantity || ''}</td><td>${s.amount}</td><td><button class='btn btn-sm btn-warning' onclick='editSale(${s.id})'>Edit</button></td>`;
        salesTableBody.appendChild(row);
      });
    }
    function renderDeliveries() {
      if (!deliveryTableBody) return;
      deliveryTableBody.innerHTML = '';
      deliveries.forEach(d => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${d.date}</td><td>${d.customer_name}</td><td>${d.product || ''}</td><td>${d.quantity || ''}</td><td>${d.status}</td><td>${d.notes || ''}</td><td><button class='btn btn-sm btn-warning' onclick='editDelivery(${d.id})'>Edit</button></td>`;
        deliveryTableBody.appendChild(row);
      });
    }
    function renderFeedback() {
      if (!feedbackTableBody) return;
      feedbackTableBody.innerHTML = '';
      feedbacks.forEach(f => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${f.date}</td><td>${f.customer_name}</td><td>${f.feedback}</td><td>${f.rating}</td><td><button class='btn btn-sm btn-warning' onclick='editFeedback(${f.id})'>Edit</button></td>`;
        feedbackTableBody.appendChild(row);
      });
    }

    // Add record handlers
    if (customerForm) {
      // Remove any existing submit event listeners (defensive, in case of hot reloads or multiple DOMContentLoaded)
      customerForm.replaceWith(customerForm.cloneNode(true));
      const newCustomerForm = document.getElementById('customerForm');
      newCustomerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const btn = newCustomerForm.querySelector('button[type="submit"]');
        if (btn) btn.disabled = true;
        const data = {
          name: newCustomerForm.name.value.trim(),
          contact: newCustomerForm.contact.value.trim(),
          email: newCustomerForm.email.value.trim(),
          address: newCustomerForm.address.value.trim()
        };
        await fetch('/api/customers', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
        newCustomerForm.reset();
        if (btn) btn.disabled = false;
        fetchCustomers();
      }, { once: true });
    }
    if (salesForm) {
      salesForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const data = {
          date: salesForm.date.value,
          customer_id: salesForm.customer.value, // Use customer_id
          product: salesForm.product.value.trim(),
          quantity: salesForm.quantity.value,
          amount: salesForm.amount.value
        };
        await fetch('/api/sales', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
        salesForm.reset();
        fetchSales();
      });
    }
    if (deliveryForm) {
      deliveryForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const data = {
          date: deliveryForm.date.value,
          customer_id: deliveryForm.customer.value, // Use customer_id
          product: deliveryForm.product.value.trim(),
          quantity: deliveryForm.quantity.value,
          status: deliveryForm.status.value,
          notes: deliveryForm.notes.value.trim()
        };
        await fetch('/api/deliveries', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
        deliveryForm.reset();
        fetchDeliveries();
      });
    }
    if (feedbackForm) {
      feedbackForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const data = {
          date: feedbackForm.date.value,
          customer_id: feedbackForm.customer.value,
          feedback: feedbackForm.feedback.value.trim(),
          rating: feedbackForm.rating.value
        };
        await fetch('/api/feedback', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
        feedbackForm.reset();
        fetchFeedback();
      });
    }

    // Edit handlers (simple prompt-based for now)
    window.editCustomer = async function(id) {
      const c = customers.find(x => x.id === id);
      if (!c) return;
      const name = prompt('Edit Name:', c.name);
      if (name === null) return;
      const contact = prompt('Edit Contact:', c.contact || '');
      if (contact === null) return;
      const email = prompt('Edit Email:', c.email || '');
      if (email === null) return;
      const address = prompt('Edit Address:', c.address || '');
      if (address === null) return;
      await fetch(`/api/customers/${id}`, {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name, contact, email, address})});
      fetchCustomers();
    };
    window.editSale = async function(id) {
      const s = sales.find(x => x.id === id);
      if (!s) return;
      const date = prompt('Edit Date:', s.date);
      if (date === null) return;
      const customer_id = prompt('Edit Customer ID:', s.customer_id);
      if (customer_id === null) return;
      const product = prompt('Edit Product:', s.product || '');
      if (product === null) return;
      const quantity = prompt('Edit Quantity:', s.quantity || '');
      if (quantity === null) return;
      const amount = prompt('Edit Amount:', s.amount);
      if (amount === null) return;
      await fetch(`/api/sales/${id}`, {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({date, customer_id, product, quantity, amount})});
      fetchSales();
    };
    window.editDelivery = async function(id) {
      const d = deliveries.find(x => x.id === id);
      if (!d) return;
      const date = prompt('Edit Date:', d.date);
      if (date === null) return;
      const customer_id = prompt('Edit Customer ID:', d.customer_id);
      if (customer_id === null) return;
      const product = prompt('Edit Product:', d.product || '');
      if (product === null) return;
      const quantity = prompt('Edit Quantity:', d.quantity || '');
      if (quantity === null) return;
      const status = prompt('Edit Status:', d.status);
      if (status === null) return;
      const notes = prompt('Edit Notes:', d.notes || '');
      if (notes === null) return;
      await fetch(`/api/deliveries/${id}`, {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({date, customer_id, product, quantity, status, notes})});
      fetchDeliveries();
    };
    window.editFeedback = async function(id) {
      const f = feedbacks.find(x => x.id === id);
      if (!f) return;
      const date = prompt('Edit Date:', f.date);
      if (date === null) return;
      const customer_id = prompt('Edit Customer ID:', f.customer_id);
      if (customer_id === null) return;
      const feedback = prompt('Edit Feedback:', f.feedback);
      if (feedback === null) return;
      const rating = prompt('Edit Rating:', f.rating);
      if (rating === null) return;
      await fetch(`/api/feedback/${id}`, {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({date, customer_id, feedback, rating})});
      fetchFeedback();
    };

    // Ensure correct rendering when switching sections
    window.showSection = function(sectionId, element) {
      // Hide all sections
      document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
      });
      // Remove active class from all nav links
      document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
      });
      // Show selected section
      const section = document.getElementById(sectionId);
      if (section) {
        section.classList.add('active');
        // If switching to customers or sales, re-render to ensure up-to-date display
        if (sectionId === 'customers') {
          renderCustomers();
        } else if (sectionId === 'sales') {
          renderCustomers(); // update dropdown
          renderSales();
        }
      }
      // Add active class to clicked nav link
      if (element) {
        element.classList.add('active');
      }
    };

    // Initial load
    fetchCustomers();
    fetchSales();
    fetchDeliveries();
    fetchFeedback();
});