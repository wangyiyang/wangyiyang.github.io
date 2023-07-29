---
layout: post
title: 如何使用 Markdown 编写数学公式
categories: Other
description: 如何使用 Markdown 编写数学公式
keywords: Markdown
mermaid: false
sequence: false
flow: false
mathjax: false
mindmap: false
mindmap2: false
---


## 1 上下标

| 算式 | Markdown |
| :---: | :---: |
| $x^2$ | `$x^2$` |
| $x_2$ | `$x_2$` |
| $x^{2+3}$ | `$x^{2+3}$` |
| $x_{2+3}$ | `$x_{2+3}$` |
| $x^{2+3}_{2+3}$ | `$x^{2+3}_{2+3}$` |
| $x^{[0]}$ | `$x^{[0]}$` |



## 2 求和

| 算式 | Markdown |
| :---: | :---: |
| $\sum_{i=1}^{n}i$ | `$\sum_{i=1}^{n}i$` |
| $\sum_{i=1}^{n}i^2$ | `$\sum_{i=1}^{n}i^2$` |
| $\sum_{i=1}^{n}i^2+1$ | `$\sum_{i=1}^{n}i^2+1$` |
| $\sum_{i=1}^{n}(i^2+1)$ | `$\sum_{i=1}^{n}(i^2+1)$` |
| $\sum_{i=1}^{n}\left(i^2+1\right)$ | `$\sum_{i=1}^{n}\left(i^2+1\right)$` |
| $\sum_{i=1}^{n}\left(i^2+1\right)^2$ | `$\sum_{i=1}^{n}\left(i^2+1\right)^2$` |
| $\sum_{i=1}^{n}\left(i^2+1\right)^2+1$ | `$\sum_{i=1}^{n}\left(i^2+1\right)^2+1$` |
| $\sum_{i=1}^{n}\left(i^2+1\right)^2+1$ | `$\sum_{i=1}^{n}\left(i^2+1\right)^2+1$` |

## 3 积分

| 算式 | Markdown |
| :---: | :---: |
| $\int_{a}^{b}f(x)dx$ | `$\int_{a}^{b}f(x)dx$` |
| $\int_{a}^{b}f(x)dx+1$ | `$\int_{a}^{b}f(x)dx+1$` |
| $\int_{a}^{b}\left(f(x)+1\right)dx$ | `$\int_{a}^{b}\left(f(x)+1\right)dx$` |
| $\int_{a}^{b}\left(f(x)+1\right)^2dx$ | `$\int_{a}^{b}\left(f(x)+1\right)^2dx$` |
| $\int_{a}^{b}\left(f(x)+1\right)^2dx+1$ | `$\int_{a}^{b}\left(f(x)+1\right)^2dx+1$` |

## 4 分数

| 算式 | Markdown |
| :---: | :---: |
| $\frac{1}{2}$ | `$\frac{1}{2}$` |
| $\frac{1}{2}+1$ | `$\frac{1}{2}+1$` |
| $\frac{1}{2}+1$ | `$\frac{1}{2}+1$` |
| $\frac{1}{2}+1$ | `$\frac{1}{2}+1$` |
| $\frac{1}{2}+1$ | `$\frac{1}{2}+1$` |
| $\frac{1-x}{y+1}$ | `$\ frac{1-x}{y+1}$` |
| $\frac{1-x}{y+1}+1$ | `$\frac{1-x}{y+1}+1$` |

## 5 根号（开方）

| 算式 | Markdown |
| :---: | :---: |
| $\sqrt{2}$ | `$\sqrt{2}$` |
| $\sqrt{2}+1$ | `$\sqrt{2}+1$` |
| $\sqrt{3}+1$ | `$\sqrt{3}+1$` |

## 6 矩阵

| 算式 | Markdown |
| :---: | :---: |
| $\begin{bmatrix}1&2&3\\4&5&6\end{bmatrix}$ | `$\begin{bmatrix}1&2&3\\4&5&6\end{bmatrix}$` |
| $\begin{bmatrix}1&2&3\\4&5&6\end{bmatrix}+1$ | `$\begin{bmatrix}1&2&3\\4&5&6\end{bmatrix}+1$` |

## 7 括号

| 算式 | Markdown |
| :---: | :---: |
| $(1+2)$ | `$(1+2)$` |
| $(1+2)+1$ | `$(1+2)+1$` |
| $f(x, y) = x^2 + y^2$ |`$f(x, y) = x^2 + y^2$`|
| $x \epsilon [0, 100]$ | `$x \epsilon [0, 100]$` |
| $y \epsilon \{1,2,3\}$ | `$y \epsilon \{1,2,3\}$` |
| $\left(\sqrt{1 \over 2}\right)^2$ | `$\left(\sqrt{1 \over 2}\right)^2$` |
| $y :\begin{cases} x+y=1\\ x-y = 0 \end{cases}$ | `$y :\begin{cases} x+y=1\\ x-y = 0 \end{cases}$` |

## 8 箭头

| 算式 | Markdown |
| :---: | :---: |
| $x \rightarrow y$ | `$x \rightarrow y$` |
| $x \leftarrow y$ | `$x \leftarrow y$` |
| $x \Rightarrow y$ | `$x \Rightarrow y$` |
| $x \Leftarrow y$ | `$x \Leftarrow y$` |
| $x \leftrightarrow y$ | `$x \leftrightarrow y$` |
| $x \Leftrightarrow y$ | `$x \Leftrightarrow y$` |


## 9 向量

| 算式 | Markdown |
| :---: | :---: |
| $\vec{a}$ | `$\vec{a}$` |
| $\vec{a}+1$ | `$\vec{a}+1$` |
| $\vec{a}+\vec{b}$ | `$\vec{a}+\vec{b}$` |
| $\vec{a}+\vec{b}+1$ | `$\vec{a}+\vec{b}+1$` |
| $\vec{a}+\vec{b}+\vec{c}$ | `$\vec{a}+\vec{b}+\vec{c}$` |

## 10 算符

| 算式 | Markdown |
| :---: | :---: |
| $x \times y$ | `$x \times y$` |
| $x \div y$ | `$x \div y$` |
| $x \pm y$ | `$x \pm y$` |
| $x \mp y$ | `$x \mp y$` |
| $x \cdot y$ | `$x \cdot y$` |
| $x \ast y$ | `$x \ast y$` |
| $x \star y$ | `$x \star y$` |
| $x \circ y$ | `$x \circ y$` |
| $x \bullet y$ | `$x \bullet y$` |
| $x \oplus y$ | `$x \oplus y$` |
| $x \ominus y$ | `$x \ominus y$` |
| $x \otimes y$ | `$x \otimes y$` |
| $x \oslash y$ | `$x \oslash y$` |
| $x \odot y$ | `$x \odot y$` |
| $x \bigodot y$ | `$x \bigodot y$` |
| $x \bigotimes y$ | `$x \bigotimes y$` |
| $x \bigoplus y$ | `$x \bigoplus y$` |
| $x \bigcup y$ | `$x \bigcup y$` |
| $x \bigcap y$ | `$x \bigcap y$` |
| $x \bigvee y$ | `$x \bigvee y$` |
| $x \bigwedge y$ | `$x \bigwedge y$` |

## 11 逻辑运算符

| 算式 | Markdown |
| :---: | :---: |
| $x \land y$ | `$x \land y$` |
| $x \lor y$ | `$x \lor y$` |
| $x \lnot y$ | `$x \lnot y$` |
| $x \forall y$ | `$x \forall y$` |
| $x \exists y$ | `$x \exists y$` |
| $x \top y$ | `$x \top y$` |
| $x \bot y$ | `$x \bot y$` |
| $x \vdash y$ | `$x \vdash y$` |
| $x \models y$ | `$x \models y$` |
| $x \vDash y$ | `$x \vDash y$` |

## 12 比较运算符

| 算式 | Markdown |
| :---: | :---: |
| $x \leq y$ | `$x \leq y$` |
| $x \geq y$ | `$x \geq y$` |
| $x \neq y$ | `$x \neq y$` |
| $x \approx y$ | `$x \approx y$` |
| $x \equiv y$ | `$x \equiv y$` |
| $x \sim y$ | `$x \sim y$` |
| $x \simeq y$ | `$x \simeq y$` |
| $x \propto y$ | `$x \propto y$` |
| $x \doteq y$ | `$x \doteq y$` |
| $x \asymp y$ | `$x \asymp y$` |
| $x \ll y$ | `$x \ll y$` |
| $x \gg y$ | `$x \gg y$` |
| $x \prec y$ | `$x \prec y$` |
| $x \succ y$ | `$x \succ y$` |
| $x \subset y$ | `$x \subset y$` |
| $x \supset y$ | `$x \supset y$` |
| $x \subseteq y$ | `$x \subseteq y$` |

## 13 集合运算符

| 算式 | Markdown |
| :---: | :---: |
| $x \cup y$ | `$x \cup y$` |
| $x \cap y$ | `$x \cap y$` |
| $x \setminus y$ | `$x \setminus y$` |
| $x \in y$ | `$x \in y$` |
| $x \notin y$ | `$x \notin y$` |
| $x \ni y$ | `$x \ni y$` |
| $x \notni y$ | `$x \notni y$` |
| $x \subset y$ | `$x \subset y$` |

## 14 累乘

| 算式 | Markdown |
| :---: | :---: |
| $\prod_{i=1}^n$ | `$\prod_{i=1}^n$` |
| $\prod_{i=1}^n x_i$ | `$\prod_{i=1}^n x_i$` |
| $\prod_{i=1}^n x_i^2$ | `$\prod_{i=1}^n x_i^2$` |

## 15 省略号

| 算式 | Markdown |
| :---: | :---: |
| $x_1, x_2, \dots, x_n$ | `$x_1, x_2, \dots, x_n$` |

## 16 三角函数

| 算式 | Markdown |
| :---: | :---: |
| $\sin x$ | `$\sin x$` |
| $\cos x$ | `$\cos x$` |
| $\tan x$ | `$\tan x$` |
| $\cot x$ | `$\cot x$` |
| $\sec x$ | `$\sec x$` |
| $\csc x$ | `$\csc x$` |
| $\arcsin x$ | `$\arcsin x$` |
| $\arccos x$ | `$\arccos x$` |
| $\arctan x$ | `$\arctan x$` |
| $\sinh x$ | `$\sinh x$` |
| $\cosh x$ | `$\cosh x$` |
| $\tanh x$ | `$\tanh x$` |
| $\coth x$ | `$\coth x$` |
| $\bot$ | `$\bot$` |
| $\angle$ | `$\angle$` |
| $30^\circ$ | `$30^\circ$` |


## 17 定积分

| 算式 | Markdown |
| :---: | :---: |
| $\infty$ | `$\infty$` |
| $y\prime$ | `$y\prime$` |
| $y\prime\prime$ | `$y\prime\prime$` |
| $\oint$| `$\oint$` |


## 18 对数

| 算式 | Markdown |
| :---: | :---: |
| $\log x$ | `$\log x$` |
| $\lg x$ | `$\lg x$` |
| $\ln x$ | `$\ln x$` |

## 19 极限

| 算式 | Markdown |
| :---: | :---: |
| $\lim_{x \to \infty}$ | `$\lim_{x \to \infty}$` |
| $\lim_{x \to 0}$ | `$\lim_{x \to 0}$` |
| $\lim_{x \to 0^+}$ | `$\lim_{x \to 0^+}$` |
| $\lim_{x \to 0^-}$ | `$\lim_{x \to 0^-}$` |

## 20 希腊字母

| 算式 | Markdown |
| :---: | :---: |
| $\alpha$ | `$\alpha$` |
| $\beta$ | `$\beta$` |
| $\gamma$ | `$\gamma$` |
| $\delta$ | `$\delta$` |
| $\epsilon$ | `$\epsilon$` |
| $\varepsilon$ | `$\varepsilon$` |
| $\zeta$ | `$\zeta$` |
| $\eta$ | `$\eta$` |
| $\theta$ | `$\theta$` |
| $\vartheta$ | `$\vartheta$` |
| $\iota$ | `$\iota$` |
| $\kappa$ | `$\kappa$` |
| $\lambda$ | `$\lambda$` |
| $\mu$ | `$\mu$` |
| $\nu$ | `$\nu$` |
| $\xi$ | `$\xi$` |
| $\pi$ | `$\pi$` |
| $\varpi$ | `$\varpi$` |
| $\rho$ | `$\rho$` |
| $\varrho$ | `$\varrho$` |
| $\sigma$ | `$\sigma$` |
| $\varsigma$ | `$\varsigma$` |
| $\tau$ | `$\tau$` |
| $\upsilon$ | `$\upsilon$` |
| $\phi$ | `$\phi$` |
| $\varphi$ | `$\varphi$` |
| $\chi$ | `$\chi$` |
| $\psi$ | `$\psi$` |
| $\omega$ | `$\omega$` |
| $\Gamma$ | `$\Gamma$` |
| $\Delta$ | `$\Delta$` |
| $\Theta$ | `$\Theta$` |
| $\Lambda$ | `$\Lambda$` |
| $\Xi$ | `$\Xi$` |
| $\Pi$ | `$\Pi$` |
| $\Sigma$ | `$\Sigma$` |
| $\Upsilon$ | `$\Upsilon$` |
| $\Phi$ | `$\Phi$` |
| $\Psi$ | `$\Psi$` |
