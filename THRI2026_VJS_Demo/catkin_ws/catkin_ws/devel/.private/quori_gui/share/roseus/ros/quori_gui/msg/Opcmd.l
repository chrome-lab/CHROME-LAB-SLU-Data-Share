;; Auto-generated. Do not edit!


(when (boundp 'quori_gui::Opcmd)
  (if (not (find-package "QUORI_GUI"))
    (make-package "QUORI_GUI"))
  (shadow 'Opcmd (find-package "QUORI_GUI")))
(unless (find-package "QUORI_GUI::OPCMD")
  (make-package "QUORI_GUI::OPCMD"))

(in-package "ROS")
;;//! \htmlinclude Opcmd.msg.html


(defclass quori_gui::Opcmd
  :super ros::object
  :slots (_data _angle_dist ))

(defmethod quori_gui::Opcmd
  (:init
   (&key
    ((:data __data) "")
    ((:angle_dist __angle_dist) 0.0)
    )
   (send-super :init)
   (setq _data (string __data))
   (setq _angle_dist (float __angle_dist))
   self)
  (:data
   (&optional __data)
   (if __data (setq _data __data)) _data)
  (:angle_dist
   (&optional __angle_dist)
   (if __angle_dist (setq _angle_dist __angle_dist)) _angle_dist)
  (:serialization-length
   ()
   (+
    ;; string _data
    4 (length _data)
    ;; float64 _angle_dist
    8
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; string _data
       (write-long (length _data) s) (princ _data s)
     ;; float64 _angle_dist
       (sys::poke _angle_dist (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; string _data
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _data (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;; float64 _angle_dist
     (setq _angle_dist (sys::peek buf ptr- :double)) (incf ptr- 8)
   ;;
   self)
  )

(setf (get quori_gui::Opcmd :md5sum-) "8e95fd03b16cd7241921e03a50a02cad")
(setf (get quori_gui::Opcmd :datatype-) "quori_gui/Opcmd")
(setf (get quori_gui::Opcmd :definition-)
      "string data
float64 angle_dist

")



(provide :quori_gui/Opcmd "8e95fd03b16cd7241921e03a50a02cad")


