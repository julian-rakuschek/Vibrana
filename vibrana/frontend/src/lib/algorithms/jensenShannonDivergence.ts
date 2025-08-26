const relative_entropy = (p: number[], q: number[]): number[] => {
    /*
    \mathrm{rel\_entr}(x, y) =
            \begin{cases}
                x \log(x / y) & x > 0, y > 0 \\
                0 & x = 0, y \ge 0 \\
                \infty & \text{otherwise}
            \end{cases}

     According to https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.rel_entr.html
     */
    if (p.length !== q.length) throw "P and Q must have the same length";
    const ent: number[] = [];

    for (let i = 0; i < p.length; i++) {
        if (p[i] > 0 && q[i] > 0) ent.push(p[i] * Math.log(p[i] / q[i]));
        else if (p[i] === 0 && q[i] >= 0) ent.push(0);
        else ent.push(Infinity);
    }

    return ent;
}

// Implementation translated from scipy's jensenShannon distance function:
// https://github.com/scipy/scipy/blob/v1.16.0/scipy/spatial/distance.py#L1303-L1388
export const jensenShannon = (p: number[], q: number[]): number => {
    if (p.length !== q.length) throw "P and Q must have the same length";

    let p_sum: number = 0;
    let q_sum: number = 0;

    for (let i = 0; i < p.length; i++) {
        p_sum += p[i];
        q_sum += q[i];
    }

    const m: number[] = [];
    for (let i = 0; i < p.length; i++) {
        p[i] /= p_sum;
        q[i] /= q_sum;
        m.push((p[i] + q[i]) / 2);
    }
    const left = relative_entropy(p, m);
    const right = relative_entropy(q, m);

    let left_sum: number = 0;
    let right_sum: number = 0;

    for (let i = 0; i < p.length; i++) {
        left_sum += left[i];
        right_sum += right[i];
    }
    const js: number = left_sum + right_sum;
    return Math.sqrt(js / 2);
}
