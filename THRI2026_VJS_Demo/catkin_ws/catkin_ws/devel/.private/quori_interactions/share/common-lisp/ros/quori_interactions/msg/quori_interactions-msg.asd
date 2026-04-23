
(cl:in-package :asdf)

(defsystem "quori_interactions-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "ArmsCmd" :depends-on ("_package_ArmsCmd"))
    (:file "_package_ArmsCmd" :depends-on ("_package"))
  ))