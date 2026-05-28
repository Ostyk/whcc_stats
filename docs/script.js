let allStatsData = null;
let currentYear = '2026'; // Default to 2026
let currentInningsRecords = [];
let currentSelectedInningsPlayer = null;

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    // Try to load from embedded script tag first (for offline/file:// access)
    const embeddedData = document.getElementById('statsData');
    if (embeddedData && embeddedData.textContent) {
        try {
            allStatsData = JSON.parse(embeddedData.textContent);
            console.log('✓ Stats loaded from embedded data');
            initializeYearSelector();
            displayStats(currentYear);
            return;
        } catch (e) {
            console.log('Failed to parse embedded data:', e);
        }
    }

    // Fallback to fetch (for server/GitHub Pages)
    loadStats();
});

async function loadStats() {
    try {
        const response = await fetch('stats.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        allStatsData = await response.json();
        console.log('✓ Stats loaded from fetch');
        initializeYearSelector();
        displayStats(currentYear);
    } catch (error) {
        console.error('Error loading stats:', error);
        const mainContent = document.querySelector('main');
        if (mainContent) {
            mainContent.innerHTML = `
                <div style="text-align: center; padding: 50px; color: #666;">
                    <h2>⚠️ Unable to Load Statistics</h2>
                    <p style="margin: 20px 0;">Could not load cricket statistics.</p>
                    <p><strong>Error:</strong> ${error.message}</p>
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                    <div style="text-align: left; max-width: 600px; margin: 0 auto; background: #f5f5f5; padding: 20px; border-radius: 8px;">
                        <p><strong>If viewing locally:</strong></p>
                        <ol>
                            <li>Make sure you're in the docs folder</li>
                            <li>Start a local server: <code style="background: white; padding: 2px 8px; border-radius: 4px;">python3 -m http.server 8000</code></li>
                            <li>Visit: <a href="http://localhost:8000">http://localhost:8000</a></li>
                        </ol>
                        <p style="margin-top: 15px;"><strong>Or:</strong> Open the browser console (F12) to see detailed errors.</p>
                    </div>
                </div>
            `;
        }
    }
}

function initializeYearSelector() {
    const yearSelect = document.getElementById('yearSelect');
    if (yearSelect && allStatsData) {
        yearSelect.value = currentYear;

        const options = yearSelect.querySelectorAll('option');
        options.forEach(option => {
            const year = option.value;
            if (!allStatsData[year] || !allStatsData[year].summary || !allStatsData[year].summary.total_matches) {
                option.disabled = true;
                option.textContent += ' (No data)';
            }
        });
    }
}

function changeYear(year) {
    currentYear = year;
    displayStats(year);
    console.log(`Switched to ${year} season`);
}

function displayStats(year) {
    const statsData = allStatsData[year];

    if (!statsData || !statsData.summary) {
        console.warn(`No data available for ${year}`);
        showNoDataMessage(year);
        return;
    }

    document.getElementById('lastUpdated').textContent = new Date(statsData.last_updated).toLocaleDateString();
    document.getElementById('totalMatches').textContent = statsData.summary.total_matches || '-';
    document.getElementById('totalRuns').textContent = statsData.summary.total_runs || '-';
    document.getElementById('totalPlayers').textContent = statsData.summary.total_players || '-';

    if (statsData.summary.date_range) {
        const start = new Date(statsData.summary.date_range.start).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
        const end = new Date(statsData.summary.date_range.end).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
        document.getElementById('dateRange').textContent = `${start} - ${end}`;
    } else {
        document.getElementById('dateRange').textContent = '-';
    }

    if (statsData.batting && statsData.batting.leaderboards) {
        displayLeaderboard('topRunScorers', statsData.batting.leaderboards.top_run_scorers,
            ['batsman', 'runs', 'innings', 'average', 'sr']);
        displayLeaderboard('highestScores', statsData.batting.leaderboards.highest_scores,
            ['batsman', 'runs', 'balls', 'sr']);
        displayLeaderboard('bestAverages', statsData.batting.leaderboards.best_averages,
            ['batsman', 'average', 'runs', 'innings']);
        displayLeaderboard('bestStrikeRates', statsData.batting.leaderboards.best_strike_rates,
            ['batsman', 'sr', 'runs', 'balls']);
        displayLeaderboard('mostFours', statsData.batting.leaderboards.most_fours,
            ['batsman', 'fours', 'runs', 'innings']);
        displayLeaderboard('mostSixes', statsData.batting.leaderboards.most_sixes,
            ['batsman', 'sixes', 'runs', 'innings']);

        displayAllPlayers(statsData.batting.season_stats);
        initializePlayerInningsExplorer(statsData.batting);
    } else {
        clearLeaderboards();
        initializePlayerInningsExplorer({ innings_records: [] });
    }

    if (statsData.bowling && statsData.bowling.leaderboards) {
        displayLeaderboard('topWicketTakers', statsData.bowling.leaderboards.top_wicket_takers,
            ['bowler', 'wickets', 'average', 'economy']);
        displayLeaderboard('bestFigures', statsData.bowling.leaderboards.best_figures,
            ['bowler', 'wickets', 'runs', 'overs']);
        displayLeaderboard('bestEconomy', statsData.bowling.leaderboards.best_economy,
            ['bowler', 'economy', 'overs', 'wickets']);
    }

    if (statsData.fielding && statsData.fielding.leaderboards) {
        displayLeaderboard('mostCatches', statsData.fielding.leaderboards.most_catches,
            ['fielder', 'catches', 'dismissals', 'matches']);
        displayLeaderboard('mostRunOuts', statsData.fielding.leaderboards.most_run_outs,
            ['fielder', 'run_outs', 'direct_hits', 'matches']);
        displayLeaderboard('mostStumpings', statsData.fielding.leaderboards.most_stumpings,
            ['fielder', 'stumpings', 'dismissals', 'matches']);
        displayLeaderboard('mostDismissalsFielding', statsData.fielding.leaderboards.most_dismissals,
            ['fielder', 'dismissals', 'catches', 'run_outs', 'stumpings']);
    }
}

function initializePlayerInningsExplorer(battingData) {
    const select = document.getElementById('playerInningsSelect');
    const title = document.getElementById('playerInningsTitle');
    const avgEl = document.getElementById('playerInningsAverage');
    const tbody = document.getElementById('playerRecentInningsBody');

    if (!select || !title || !avgEl || !tbody) return;

    currentInningsRecords = (battingData && battingData.innings_records) ? battingData.innings_records : [];

    if (currentInningsRecords.length === 0) {
        select.innerHTML = '';
        title.textContent = 'Recent innings';
        avgEl.textContent = 'Average: -';
        currentSelectedInningsPlayer = null;
        setExplorerSummary(null);
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #888;">No innings data</td></tr>';
        return;
    }

    const currentSelection = select.value;
    const players = [...new Set(currentInningsRecords.map(r => r.batsman))].sort((a, b) => a.localeCompare(b));
    select.innerHTML = players.map(player => `<option value="${player}">${player}</option>`).join('');

    if (currentSelection && players.includes(currentSelection)) {
        select.value = currentSelection;
    } else {
        select.value = players[0];
    }

    renderPlayerRecentInnings();
}

function renderPlayerRecentInnings() {
    const select = document.getElementById('playerInningsSelect');
    const limitInput = document.getElementById('inningsLimit');
    const title = document.getElementById('playerInningsTitle');
    const avgEl = document.getElementById('playerInningsAverage');
    const tbody = document.getElementById('playerRecentInningsBody');

    if (!select || !limitInput || !title || !avgEl || !tbody) return;

    const selectedPlayer = select.value;

    if (!selectedPlayer) {
        avgEl.textContent = 'Average: -';
        currentSelectedInningsPlayer = null;
        setExplorerSummary(null);
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #888;">Select a player</td></tr>';
        return;
    }

    const playerAllRows = currentInningsRecords.filter(r => r.batsman === selectedPlayer);
    const maxAvailable = Math.max(1, playerAllRows.length);
    limitInput.max = String(maxAvailable);

    // Default to full player season (max innings) when player changes.
    if (currentSelectedInningsPlayer !== selectedPlayer) {
        limitInput.value = String(maxAvailable);
        currentSelectedInningsPlayer = selectedPlayer;
    }

    const limit = Math.max(1, Math.min(maxAvailable, parseInt(limitInput.value || String(maxAvailable), 10)));
    limitInput.value = limit;

    const rows = playerAllRows
        .sort((a, b) => new Date(b.match_date) - new Date(a.match_date))
        .slice(0, limit);

    title.textContent = `${selectedPlayer} - last ${rows.length} innings`;

    const totalRuns = rows.reduce((sum, row) => sum + (Number(row.runs) || 0), 0);
    const totalBalls = rows.reduce((sum, row) => sum + (Number(row.balls) || 0), 0);
    const totalFours = rows.reduce((sum, row) => sum + (Number(row.fours) || 0), 0);
    const totalSixes = rows.reduce((sum, row) => sum + (Number(row.sixes) || 0), 0);
    const outs = rows.filter(row => !String(row.status || '').toLowerCase().includes('not out')).length;
    const avg = outs > 0 ? (totalRuns / outs) : totalRuns;
    const strikeRate = totalBalls > 0 ? (totalRuns / totalBalls) * 100 : 0;
    avgEl.textContent = `Average over selected innings: ${avg.toFixed(2)} (runs: ${totalRuns}, outs: ${outs})`;
    setExplorerSummary({
        avgRuns: avg,
        strikeRate,
        totalRuns,
        totalBalls,
        totalFours,
        totalSixes
    });

    if (rows.length === 0) {
        avgEl.textContent = 'Average: -';
        setExplorerSummary(null);
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #888;">No innings found</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    rows.forEach(inn => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${formatValue(inn.match_date)}</td>
            <td>${formatValue(inn.file)}</td>
            <td>${formatValue(inn.runs, 'runs')}</td>
            <td>${formatValue(inn.balls, 'balls')}</td>
            <td>${formatValue(inn.fours, 'fours')}</td>
            <td>${formatValue(inn.sixes, 'sixes')}</td>
            <td>${formatValue(inn.sr, 'sr')}</td>
            <td>${formatValue(inn.status)}</td>
        `;
        tbody.appendChild(tr);
    });
}

function setExplorerSummary(summary) {
    const ids = {
        avgRuns: 'explorerAvgRuns',
        strikeRate: 'explorerSR',
        totalRuns: 'explorerTotalRuns',
        totalBalls: 'explorerTotalBalls',
        totalFours: 'explorerTotalFours',
        totalSixes: 'explorerTotalSixes'
    };

    if (!summary) {
        Object.values(ids).forEach(id => {
            const el = document.getElementById(id);
            if (el) el.textContent = '-';
        });
        return;
    }

    const avgEl = document.getElementById(ids.avgRuns);
    const srEl = document.getElementById(ids.strikeRate);
    const runsEl = document.getElementById(ids.totalRuns);
    const ballsEl = document.getElementById(ids.totalBalls);
    const foursEl = document.getElementById(ids.totalFours);
    const sixesEl = document.getElementById(ids.totalSixes);

    if (avgEl) avgEl.textContent = Number(summary.avgRuns).toFixed(2);
    if (srEl) srEl.textContent = Number(summary.strikeRate).toFixed(2);
    if (runsEl) runsEl.textContent = Math.round(summary.totalRuns).toString();
    if (ballsEl) ballsEl.textContent = Math.round(summary.totalBalls).toString();
    if (foursEl) foursEl.textContent = Math.round(summary.totalFours).toString();
    if (sixesEl) sixesEl.textContent = Math.round(summary.totalSixes).toString();
}

function showNoDataMessage(year) {
    const tables = document.querySelectorAll('table tbody');
    tables.forEach(tbody => {
        tbody.innerHTML = `
            <tr>
                <td colspan="10" style="text-align: center; padding: 20px; color: #888;">
                    No data available for ${year} season yet
                </td>
            </tr>
        `;
    });

    document.getElementById('dateRange').textContent = 'No matches yet';
}

function clearLeaderboards() {
    const tables = ['topRunScorers', 'highestScores', 'bestAverages', 'bestStrikeRates',
                    'mostFours', 'mostSixes', 'topWicketTakers', 'bestFigures', 'bestEconomy',
                    'mostCatches', 'mostRunOuts', 'mostStumpings', 'mostDismissalsFielding'];
    tables.forEach(tableId => {
        const tbody = document.querySelector(`#${tableId} tbody`);
        if (tbody) tbody.innerHTML = '';
    });
}

function displayLeaderboard(tableId, data, columns) {
    const tbody = document.querySelector(`#${tableId} tbody`);
    if (!tbody) return;

    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; color: #888;">No data</td></tr>';
        return;
    }

    window._leaderboardState = window._leaderboardState || {};
    // Preserve showAll across year changes; reset only on first load of this table
    const prev = window._leaderboardState[tableId];
    window._leaderboardState[tableId] = { data, columns, tbody, showAll: prev ? prev.showAll : false };
    renderLeaderboard(tableId);
}

function renderLeaderboard(tableId) {
    const state = window._leaderboardState && window._leaderboardState[tableId];
    if (!state) return;
    const { data, columns, tbody, showAll } = state;
    const DEFAULT_ROWS = 10;

    tbody.innerHTML = '';
    const visible = showAll ? data : data.slice(0, DEFAULT_ROWS);
    visible.forEach((row, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${index + 1}</td>
            ${columns.map(col => `<td>${formatValue(row[col], col)}</td>`).join('')}
        `;
        tbody.appendChild(tr);
    });

    if (data.length > DEFAULT_ROWS) {
        const toggleRow = document.createElement('tr');
        toggleRow.innerHTML = `
            <td colspan="${columns.length + 1}" style="text-align:center; padding: 10px;">
                <button onclick="toggleLeaderboard('${tableId}')"
                    style="background:none; border:1px solid #667eea; color:#667eea;
                           padding:5px 16px; border-radius:6px; cursor:pointer; font-size:0.9em;">
                    ${showAll ? '&#9650; Show top 10' : '&#9660; Show all ' + data.length}
                </button>
            </td>`;
        tbody.appendChild(toggleRow);
    }
}

function toggleLeaderboard(tableId) {
    const state = window._leaderboardState && window._leaderboardState[tableId];
    if (!state) return;
    state.showAll = !state.showAll;
    renderLeaderboard(tableId);
}

function displayAllPlayers(players) {
    const tbody = document.getElementById('allPlayersList');
    if (!tbody) return;

    if (!players || players.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" style="text-align: center; color: #888;">No players</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    players.forEach(player => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${player.batsman}</td>
            <td>${formatValue(player.innings, 'innings')}</td>
            <td>${formatValue(player.runs, 'runs')}</td>
            <td>${formatValue(player.average, 'average')}</td>
            <td>${formatValue(player.sr, 'sr')}</td>
            <td>${formatValue(player.balls, 'balls')}</td>
            <td>${formatValue(player.fours, 'fours')}</td>
            <td>${formatValue(player.sixes, 'sixes')}</td>
            <td>${formatValue(player.avg_batting_position, 'avg_batting_position')}</td>
            <td>${formatValue(player.avg_overs_per_game, 'avg_overs_per_game')}</td>
        `;
        tbody.appendChild(tr);
    });
}

function formatValue(val, columnName) {
    if (val === null || val === undefined) return '-';
    if (typeof val === 'number') {
        if (isNaN(val)) return '-';

        const integerFields = ['runs', 'innings', 'balls', 'fours', 'sixes', 'wickets', 'overs', 'maidens'];
        if (columnName && integerFields.includes(columnName)) {
            return Math.round(val).toString();
        }

        return val.toFixed(2);
    }
    return val;
}

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

function filterPlayers() {
    const searchTerm = document.getElementById('playerSearch').value.toLowerCase();
    const rows = document.querySelectorAll('#allPlayersList tr');

    rows.forEach(row => {
        const playerName = row.cells[0].textContent.toLowerCase();
        row.style.display = playerName.includes(searchTerm) ? '' : 'none';
    });
}

function sortTable(columnIndex) {
    const table = document.getElementById('allPlayersTable');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const aVal = a.cells[columnIndex].textContent;
        const bVal = b.cells[columnIndex].textContent;
        const aNum = parseFloat(aVal);
        const bNum = parseFloat(bVal);

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return bNum - aNum;
        }

        return aVal.localeCompare(bVal);
    });

    rows.forEach(row => tbody.appendChild(row));
}
