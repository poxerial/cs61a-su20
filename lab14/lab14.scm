(define (split-at lst n)
  (define (split-at-helper lst n first)
    (if (or (= n 0) (null? lst))
        (cons first lst)
        (split-at-helper (cdr lst)
                         (- n 1)
                         (append first (list (car lst))))))
  (split-at-helper lst n nil))

; Tree Abstraction
; Constructs tree given label and list of branches
(define (tree label branches)
  (cons label branches))

; Returns the label of the tree
(define (label t) (car t))

; Returns the list of branches of the given tree
(define (branches t) (cdr t))

; Returns #t if t is a leaf, #f otherwise
(define (is-leaf t) (null? (branches t)))

(define (filter-odd t)
  (if (= (modulo (label t) 2) 1)
      (tree (label t) (map filter-odd (branches t)))
      (tree nil (map filter-odd (branches t)))))

(define (cddr s) (cdr (cdr s)))

(define (cadr s) (car (cdr s)))

(define (caddr s) (car (cddr s)))

(define (swap expr)
  (if (< (eval (cadr expr)) (eval (caddr expr)))
      (cons (car expr)
            (cons (caddr expr)
                  (cons (cadr expr) (cdr (cddr expr)))))
        expr))
