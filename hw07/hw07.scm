(define (cadr lst) (car (cdr lst)))

(define (make-kwlist1 keys values)
  (list keys values))

(define (get-keys-kwlist1 kwlist) (car kwlist))

(define (get-values-kwlist1 kwlist) (cadr kwlist))

(define (make-kwlist2 keys values)
  (if (or (null? keys) (null? values))
      nil
      (cons (list (car keys) (car values))
            (make-kwlist2 (cdr keys) (cdr values)))))

(define (get-keys-kwlist2 kwlist)
  (if (null? kwlist)
      nil
      (cons (car (car kwlist))
            (get-keys-kwlist2 (cdr kwlist)))))

(define (get-values-kwlist2 kwlist)
  (if (null? kwlist)
      nil
      (cons (cadr (car kwlist))
            (get-values-kwlist2 (cdr kwlist)))))

(define (add-to-kwlist kwlist key value)
  (make-kwlist
   (append (get-keys-kwlist kwlist) (list key))
   (append (get-values-kwlist kwlist) (list value))))

(define (get-first-from-kwlist kwlist key)
  (cond 
    ((null? (get-keys-kwlist kwlist))
     nil)
    ((eq? (car (get-keys-kwlist kwlist)) key)
     (car (get-values-kwlist kwlist)))
    (else
     (get-first-from-kwlist
      (make-kwlist (cdr (get-keys-kwlist kwlist))
                   (cdr (get-values-kwlist kwlist)))
      key))))

(define (prune-expr expr)
  (define (prune-helper lst)
    (cond 
      ((null? lst)
       nil)
      ((null? (cdr lst))
       (list (car lst)))
      (else
       (cons (car lst) (prune-helper (cdr (cdr lst)))))))
  (append (list (car expr))
          (prune-helper (cdr expr))))

(define (curry-cook formals body)
  (if (null? (cdr formals))
      (list 'lambda (list (car formals)) body)
      (list 'lambda
            (list (car formals))
            (curry-cook (cdr formals) body))))

(define (curry-consume curries args)
  (if (null? (cdr args))
      (curries (car args))
      (curry-consume (curries (car args)) (cdr args))))
