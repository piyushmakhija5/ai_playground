export async function fetchHint() {
    const res = await fetch('/api/hint', {
      method: 'POST',
    });
    return res.json();
  }
  
  export async function fetchSolution() {
    const res = await fetch('/api/solve', {
      method: 'POST',
    });
    return res.json();
  }
  