(define (cddr s) (cdr (cdr s)))

(define (cadr s) (car (cdr s)))

(define (caddr s) (car (cddr s)))

(define (ascending? lst)
  (or (null? lst)
      (null? (cdr lst))
      (and (or (< (car lst) (cadr lst))
               (= (car lst) (cadr lst)))
           (ascending? (cdr lst)))))

(define (interleave lst1 lst2)
  (cond 
    ((null? lst1)
     lst2)
    ((null? lst2)
     lst1)
    (#t
     (cons (car lst1) (interleave lst2 (cdr lst1))))))

(define (my-filter func lst)
  (if (null? lst)
      lst
      (if (func (car lst))
          (cons (car lst) (my-filter func (cdr lst)))
          (my-filter func (cdr lst)))))

(define (no-repeats lst)
  (define (in-list item l)
    (if (null? l)
        #f
        (if (= item (car l))
            #t
            (in-list item (cdr l)))))
  (define (no-repeats-core lst rst)
    (if (null? lst)
        rst
        (if (in-list (car lst) rst)
            (no-repeats-core (cdr lst) rst)
            (no-repeats-core (cdr lst)
                             (append rst (list (car lst)))))))
  (no-repeats-core lst nil))
