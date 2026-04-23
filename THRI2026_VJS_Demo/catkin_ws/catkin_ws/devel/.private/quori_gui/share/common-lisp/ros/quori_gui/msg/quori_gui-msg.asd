
(cl:in-package :asdf)

(defsystem "quori_gui-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "Opcmd" :depends-on ("_package_Opcmd"))
    (:file "_package_Opcmd" :depends-on ("_package"))
  ))